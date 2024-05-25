from datetime import timedelta
import csv
import os
import shutil
from StringIO import StringIO
import time

HISTORY_BASE_FIELDS = ['data_counter', 'unix_time', 'year', 'month', 'day', 'hour', 'minute', 'second', 'timezone', 'volume', 'open_interest'] # Added May 25 - added open_interest

class HistoryDataFileSet():
    def __init__(self, candidate_fields, my_root, csv_names, rewrite_mismatching_headers=False):
        self.candidate_fields = candidate_fields
        self.my_root = my_root
        self.csv_names = csv_names
        self.init_all(rewrite_mismatching_headers)

    def get_dir_path(self):
        return os.path.join('temp_server/', self.my_root, 'price_logs')

    def _check_base_fields(self, fieldnames):
        # Check if the field names in the file that's been read matches with HISTORY_BASE_FIELDS. That is to say, everything
        # that comes before the candidate names. This is useful when we change the csv format. It will stop us from accidentally
        # writing things in the wrong format.

        fieldnames_expected_base = fieldnames[:len(HISTORY_BASE_FIELDS)]
        if fieldnames_expected_base != HISTORY_BASE_FIELDS:
            raise Exception(
                "Discrepancy in HISTORY_BASE_FIELDS from read file. Expected: \n" +
                repr(HISTORY_BASE_FIELDS) +
                "\n Got: \n" +
                repr(fieldnames_expected_base)
            )

    def get_file_fields(self):
        fields = HISTORY_BASE_FIELDS + self.candidate_fields
        assert len(fields) == len(set(fields)), (
            "CSV File Headers: A candidate's name was duplicated, or collides with one of the HISTORY_BASE_FIELDS: " +
            repr(self.candidate_fields)
        )
        return fields

    def get_file_name(self, csv_name):
        # Sanity check, before going about creating random files:
        assert csv_name in self.csv_names 
        # Within data dir, lower case and add extension. MARKET_BLAH becomes market_blah.csv
        return os.path.join(self.get_dir_path(), csv_name.lower() + '.csv')

    def init_all(self, rewrite_mismatching_headers):
        "Make sure data dir exists and all data files are initialized, and header names are updated"

        history_dir_path = self.get_dir_path()

        # Create data dir
        if not os.path.exists(history_dir_path):
            os.mkdir(history_dir_path)

        history_file_fields = self.get_file_fields()

        for csv_name in self.csv_names:
            csv_file_name = self.get_file_name(csv_name)
            rewriting_headers_csv_file_name = csv_file_name + ".rewriting_headers"

            # Create csv files that don't yet exist, and write the header row
            if not os.path.exists(csv_file_name):
                with open(csv_file_name, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=history_file_fields)
                    writer.writeheader()

            # Add newline at the end if csv is missing it (This was a problem with csv files edited with Excel etc)
            missing_newline = False
            with open(csv_file_name, 'r') as csvfile:
                for line in csvfile:
                    pass
                if line[-1] != '\n':
                    missing_newline = True
            if missing_newline:
                print csv_file_name, 'missing newline. Adding now.'
                with open(csv_file_name, 'a') as csvfile:
                    csvfile.write("\n")

            # Update csv files whose headers have changed
            headers_match = True
            with open(csv_file_name, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                self._check_base_fields(reader.fieldnames)
                headers_match = (reader.fieldnames == history_file_fields)

            if not headers_match:
                if not rewrite_mismatching_headers:
                    raise Exception("Mismatching headers for %s. Not rewriting headers." % csv_file_name)
                print "Rewriting headers for %s! This could take a minute because it has to copy all the data to a new file." % csv_file_name
                print "Temporarily putting the result in %s." % rewriting_headers_csv_file_name

                # Write the new header using the csv library (for simplicity and consistency)
                with open(rewriting_headers_csv_file_name, 'w') as csvfilerewriteheaders:
                    writer = csv.DictWriter(csvfilerewriteheaders, fieldnames=history_file_fields)
                    writer.writeheader()

                # Copy the data directly, line by line, for speed
                with open(csv_file_name, 'r') as csvfile:
                    csvfile.next() # Drop the header row
                    with open(rewriting_headers_csv_file_name, 'a') as csvfilerewriteheaders:
                        for row in csvfile:
                            csvfilerewriteheaders.write(row)
                shutil.move(rewriting_headers_csv_file_name, csv_file_name)

    # ADDED May 25
    # Add the open_interest column and its data
    def write_for_csv_name(self, csv_name, data_counter, unix_time, local_time, odds_data, volume, open_interest):
        """
        `odds_data` should be a list of numbers or `None` values. `None` values will result in an empty cell. Numbers will be truncated before saving.
        """

        if not type(unix_time) == int:
            raise TypeError("write_for_csv_name: unix_time should be an int")

        assert len(odds_data) == len(self.candidate_fields), "Save to CSV: Odds count don't match candidate count"

        truncated_odds_data = [
            round(item, 4) if item is not None else None
            for item
            in odds_data
        ]

        row_data = {
            self.candidate_fields[candidate_index]: datum
            for candidate_index, datum in enumerate(truncated_odds_data)
        }

        row_data['data_counter'] = data_counter
        row_data['unix_time'] = unix_time

        # Human-readable and sortable time fields
        row_data['year'] = local_time.year
        row_data['month'] = local_time.month
        row_data['day'] = local_time.day
        row_data['hour'] = local_time.hour
        row_data['minute'] = local_time.minute
        row_data['second'] = local_time.second
        row_data['timezone'] = time.strftime('%Z')

        row_data['volume'] = int(round(volume))
        row_data['open_interest'] = int(round(open_interest)) # Added may 25 - added open_interest

        csv_file_name = self.get_file_name(csv_name)
        with open(csv_file_name, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.get_file_fields())
            # NOTE: DictWriter writes extra commas for unused columns. We will get rid of the unused candidate columns soon.
            writer.writerow(row_data)

    def read_for_csv_name(self, csv_name, timespan_to_load, unix_time):
        """
        Returns the requested number of days worth of data history for the given
        csv file.
        """
        csv_file_name = self.get_file_name(csv_name)
        with open(csv_file_name, 'r') as csvfile:

            # "Manually" Pre-parse the CSV file and throw out the lines we don't need before putting it into
            #   Python's csv library, so that it's not all in memory and super slow.
            # As we read through the file, we want to keep:
            # * The last so many lines of the file (saved in `loaded_lines`)
            # * The "headers" line of the file, to combine with `loaded_lines` to make a truncated csv file
            #   (in memory, not saved anywhere) that we will load into Python's csv library.
            # * The first line of data in the file, just to extract the unix_time so we know how long we have been tracking data

            headers_line = csvfile.next()

            # Check to make sure the CSV format hasn't drastically changed. If `data_counter` and `unix_time` are not the first two columns,
            # I worry about simply doing `split(',')` to find it. Maybe a comma will end up in someone's name or something.
            unix_time_col_index = headers_line.split(',').index('unix_time')
            assert unix_time_col_index == 1, "CSV format seems to have changed. See comment in code."
            assert headers_line.split(',').index('data_counter') == 0, "CSV format seems to have changed. See comment in code."

            target_start_unix_time = unix_time - timespan_to_load.total_seconds()
            first_line = None
            loaded_lines = [] # The lines at the end of the CSV data that we keep
            for line_index, line in enumerate(csvfile):
                if line_index == 0:
                    first_line = line
                loaded_lines.append(line)
                if line_index % 1000 == 0 and int(line.split(',')[unix_time_col_index]) < target_start_unix_time:
                    # `line` is still before the target start unix time. This means we
                    # don't need anything in loaded_lines thus far, so let's flush it
                    # to save memory.
                    #
                    # We're only doing this only every 1000 lines because doing it every
                    # line would slow things down. 999 extra lines in memory is not a
                    # problem.
                    loaded_lines = []

            data_history = DataHistory(self.candidate_fields)

            # Set the unix start time if we have any data. If there is no data, we leave it set
            # to None, and get_time_since_start knows what to do with it.
            if first_line is not None:
                end_of_csv_file = StringIO(headers_line + first_line)
                reader = csv.DictReader(end_of_csv_file)
                data_history.start_unix_time = int(reader.next()['unix_time'])

            # TODO - After I read the non-crazy-long history, convert all unix_times to ints upfront

            # Create a csv file-like-object in memory, which contains the headers and loaded_lines
            # Then, make a csv DictReader as usual. It'll use the headers and know what to do.
            end_of_csv_file = StringIO(headers_line + ''.join(loaded_lines))
            reader = csv.DictReader(end_of_csv_file)
            data_history.entries = list(reader)

            return data_history

    # This tests the history finding function. For now we just have to look at the output.
    # This (along with lots of other things) belongs in a separate file. All in good time.
    def test_history(self):
        data_history = DataHistory([])
        data_history.entries = [
                {'unix_time': '100'},
                {'unix_time': '200'},
                {'unix_time': '250'},
            ]

        # {the time we're searching for: the time of the entry we expect to get}
        expected = {
            1: 100,
            2: 100,
            99: 100,
            100: 100,
            110: 100,
            145: 100,
            149: 100,
            150: 100,
            151: 200,
            175: 200,
            195: 200,
            199: 200,
            200: 200,
            201: 200,
            210: 200,
            220: 200,
            225: 200,
            240: 250,
            249: 250,
            250: 250,
            251: 250,
            260: 250,
            280: 250,
            300: 250,
            1000: 250,
        }

        print 'Testing finding nearest entry:'

        for search_unix_time, expected_unix_time in expected.iteritems():
            entry = data_history._find_nearest_entry(search_unix_time)
            assert expected_unix_time == int(entry['unix_time']), "Requesting for time %s, expected %s, got %s" % (
                search_unix_time, expected_unix_time, entry['unix_time'])

        raise Exception('DONE WITH TEST')

# A structure holding all the DataHistory we'll need for the given run. Sometimes we may want multiple.
class DataHistory:

    def __init__(self, candidate_fields):
        # The first unix_time in the file
        self.start_unix_time = None

        # The latest entries, covering the time span we requested.
        self.entries = []

        self.candidate_fields = candidate_fields

    def get_next_data_counter(self):
        if len(self.entries) == 0:
            last_data_counter = 0
        else:
            last_data_counter = int(self.entries[-1]['data_counter'])
        return last_data_counter + 1

    def get_time_since_start(self, unix_time):
        if self.start_unix_time is None:
            return timedelta(0)
        else:
            return timedelta(seconds=unix_time - self.start_unix_time)

    def get_time_since_last_data(self, unix_time):
        # Iterate backwards until we find an entry with actual data
        for entry in self.entries[::-1]:
            if any(entry[field] for field in self.candidate_fields):
                return timedelta(seconds=unix_time - int(entry['unix_time']))

        # If we find no entries with data...
        return None

    def _find_nearest_entry_index(self, target_unix_time):
        if len(self.entries) == 0:
            # We have no entries, indicate nothing found
            return None

        if target_unix_time <= int(self.entries[0]['unix_time']):
            # We are asking for something before or equal to the first entry, so the first entry has to be the best match.
            return 0

        if target_unix_time >= int(self.entries[-1]['unix_time']):
            # We are asking for something after or equal to the last entry (perhaps we had a lapse in saving data),
            # so the last entry has to be the best match.
            # Don't return -1 because we do math on the index
            return len(self.entries) - 1

        next_entries = iter(self.entries)
        next_entries.next()
        # This iterates every entry along with the next entry. Convenient for our checks.
        for index, (entry, next_entry) in enumerate(zip(self.entries, next_entries)):
            next_entry_unix_time = int(next_entry['unix_time'])
            if next_entry_unix_time < target_unix_time:
                # The next entry is still earlier than the one we're looking for.
                # Try the next one.
                continue

            # At this point, the current entry is earlier than target unix time,
            # but the next entry is equal to or later. Assuming the timestamps are properly in
            # order in the file, this means that either entry or next_entry is the closest match.
            # Let's find out which one has a bigger time difference.

            entry_unix_time = int(entry['unix_time'])
            if target_unix_time - entry_unix_time > next_entry_unix_time - target_unix_time:
                return index + 1
            else:
                return index

        raise Exception(
            """If we got here, there's a problem in the code, or maybe the unix
            times in the csv are out of order."""
        )

    def _find_nearest_entry(self, target_unix_time):
        found_index = self._find_nearest_entry_index(target_unix_time)
        if found_index is None:
            # We have no data yet. Return a dummy entry.
            return {}

        return self.entries[found_index]

    def _find_nearest_entries(self, target_unix_time, entries_before_and_after):
        found_index = self._find_nearest_entry_index(target_unix_time)

        if found_index is None:
            return [] # No entries found

        start_index = max(found_index - entries_before_and_after, 0)
        end_index = min(found_index + entries_before_and_after, len(self.entries) - 1)

        return self.entries[start_index: end_index + 1]

    @staticmethod
    def _get_cleaned_value(entry, field):
        # NOTE We indicate *missing* historical values with `None`. For instance, {my_candidate: None}. This is different from 0, such as {my_candidate: 0}.
        # * If a historical value is *missing*, we can't use it as the basis of a diff with the current value.
        #   * In this case, we probably display 0% for the diff, for lack of better option.
        # * If this historical value is actually 0, that's a known value that we can use to make a diff.
        #   * In that case, diff = current_value - 0 = current_value

        if field not in entry:
            # I think this only happens in the first run, thus we have no data yet whatsoever
            return None

        raw_value = entry[field]
        if raw_value is None:
            # It's a new column added to the end
            return None
        if raw_value == '':
            # A previously existing column had no data entered for the given row
            return None

        return float(raw_value)

    def get_past_win_odds(self, unix_time, desired_delay):
        # unix_time is the timestamp as the program is running
        # desired_delay is a timedelta representing how far back in time to go to look for a closest match entry

        entry = self._find_nearest_entry(unix_time - desired_delay.total_seconds())

        return {
            candidate_field: self._get_cleaned_value(entry, candidate_field)
            for candidate_field in self.candidate_fields
        }

    def get_past_win_odds_row(self, unix_time, desired_delay):
        entry = self.get_past_win_odds(unix_time, desired_delay)
        return [
            entry[candidate_field] for candidate_field in self.candidate_fields
        ]

    def get_past_volumes(self, unix_time, desired_delay, entries_before_and_after):
        # unix_time is the timestamp as the program is running
        # desired_delay is a timedelta representing how far back in time to go to look for a closest match entry

        nearest_entries = self._find_nearest_entries(unix_time - desired_delay.total_seconds(), entries_before_and_after)

        return [
            self._get_cleaned_value(entry, "volume")
            for entry in nearest_entries
        ]

    ####################
    ### ADDED May 25 ###
    ####################
    def get_past_open_interests(self, unix_time, desired_delay, entries_before_and_after):
        # unix_time is the timestamp as the program is running
        # desired_delay is a timedelta representing how far back in time to go to look for a closest match entry

        nearest_entries = self._find_nearest_entries(unix_time - desired_delay.total_seconds(), entries_before_and_after)

        return [
            self._get_cleaned_value(entry, "open_interest")
            for entry in nearest_entries
        ]
    ############

    def has_data(self):
        return len(self.entries) > 0

    # From the *current time*, not from the last entry
    def timespan_loaded(self, unix_time):
        if self.has_data():
            return timedelta(seconds=unix_time - int(self.entries[0]['unix_time']))
        else:
            return timedelta(0)