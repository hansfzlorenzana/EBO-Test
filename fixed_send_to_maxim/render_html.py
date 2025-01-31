def arrowfinder(a):
    if a <= -.0005:
        a = '<img src="red.png" width="20" height="20">'
    elif a >= 0.0005:
        a = '<img src="green.png" width="20" height="20"> '
    elif a >= 0 and a < .001:
        a = '+'
    else:
        a = ""
    return a

def first_candidate_row(
        cand_name,
        odds_percentage,
        change_percentage,
        arrow_img,
        link_open_tag,
        button,
        my_html_address,
        tooltip_text,
        tooltip_visible,

        # Optional parameter(s) start here
        odds_color=None,
    ):
    
    if odds_color is None:
        odds_color = 'rgb(0, 0, 0)'

    return '''
            <tr>
                <td align="right" bgcolor="#FFFFFF">{link_open_tag}
                    <div class="candidate-tooltip"><b><u>
                        <span style="font-size: 21pt;">
                            <img src="/{cand_name}.png" width="100" height="140">
                        </span>
                        <span class="tooltiptext" style="{tooltip_visibility}">{tooltip_text}</span>
                    </u></b></div>
                </a></td>
                <td bgcolor="#FFFFFF">
                    <p style="font-size: 55pt; margin-bottom:-10px; color: {odds_color};">{odds_percentage}%</p>
                    <span style="font-size: 20pt; color: {odds_color};">{arrow_img}{change_percentage}%</span>
                    <span style="font-size: 12.5pt;">
                        <select onChange="window.location.href=this.value">
                            {button}
                            <option value="/{my_html_address}.html#chart"">CHARTS</option>
                        </select>
                    </span>
                </td>
            </tr>
            '''.format(
        cand_name=cand_name,
        odds_percentage=odds_percentage,
        change_percentage=change_percentage,
        arrow_img=arrow_img,
        link_open_tag=link_open_tag,
        button=button,
        my_html_address=my_html_address,
        tooltip_text=tooltip_text,
        tooltip_visibility="display:none;" if not tooltip_visible else "",
        odds_color=odds_color,
    )

def next_candidate_row(
        cand_name,
        odds_percentage,
        change_percentage,
        arrow_img,
        link_open_tag,
        button,
        my_html_address,
        tooltip_text,
        tooltip_visible,

        # Optional parameter(s) start here
        odds_color=None,
    ):
    if odds_color is None:
        odds_color = 'rgb(0, 0, 0)'

    return '''
                <tr>
                    <td align="right" bgcolor="#FFFFFF">{link_open_tag}
                        <div class="candidate-tooltip"><b><u>
                            <span style="font-size: 21pt;">
                                <img src="/{cand_name}.png" width="100" height="140">
                            </span>
                            <span class="tooltiptext" style="{tooltip_visibility}">{tooltip_text}</span>
                        </u></b></div>
                    </a></td>
                    <td bgcolor="#FFFFFF">
                        <p style="font-size: 55pt; margin-bottom:-10px; color: {odds_color};">{odds_percentage}%</p>
                        <span style="font-size: 20pt; color: {odds_color};">{arrow_img}{change_percentage}%</span>
                    </td>
                </tr>
                '''.format(
        cand_name=cand_name,
        odds_percentage=odds_percentage,
        change_percentage=change_percentage,
        arrow_img=arrow_img,
        link_open_tag=link_open_tag,
        button=button, # Unused
        my_html_address=my_html_address,
        tooltip_text=tooltip_text,
        tooltip_visibility="display:none;" if not tooltip_visible else "",
        odds_color=odds_color,
    )

def page(
        now,
        Nav_bar,
        Chart_nav_bar,
        Ad_bar,
        Other_bar,
        column_title,
        race_description,
        publishable_total_volume,
        rows_created,
        chart_rows_created,
        WIN_ingested_data,
        formatted_WIN_chart_data,
        chart_colors,
        chart_label_ordering,

        # Optional parameter(s) start here
        chance_of_text=None,
        chance_of_text_extra_html='',
    ):

    if publishable_total_volume:
        total_volume_line = '$' + str(publishable_total_volume)+' bet so far'
    else:
        total_volume_line = ''

    if chance_of_text is None:
        chance_of_text = 'Chance of...'

    return ('''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
                <html>
                <head>
                <!-- Google tag (gtag.js) -->
                <script async src="https://www.googletagmanager.com/gtag/js?id=G-PSSMNJWYG3"></script>
                <script>
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', 'G-PSSMNJWYG3');
                </script>
                
                <title>Election Betting Odds by Maxim Lott and John Stossel</title>
                <meta name="description" content="Live betting odds on the 2024 presidential election, and more! Who will win? Biden, Trump, Harris, DeSantis?...">
                <meta name="author" content="Maxim Lott">
                <meta property="fb:admins" content="maxim.lott" />
                <meta property="og:title" content="Election Betting Odds" />
                <meta property="og:description" content="Live betting odds on the 2024 presidential election, and more! Who will win? Biden, Trump, Harris, DeSantis?..." />
                <meta property="og:type" content="website" />
                <meta property="og:image" content="http://maximwebsite.tripod.com/pngthumb2024.png" />
                <meta property="og:url" content="http://www.electionbettingodds.com" />
                <meta property="og:site_name" content="Election Betting Odds by Maxim Lott and John Stossel" />

                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:site" content="@maximlott">
                <meta name="twitter:creator" content="@maximlott">
                <meta name="twitter:title" content="Live Election Betting Odds">
                <meta name="twitter:description" content="Live betting odds on the 2024 presidential election, and more! Who will win? Biden, Trump, Harris, DeSantis?... Click to find out">
                <meta name="twitter:image" content="http://maximwebsite.tripod.com/pngthumb2024.png">

                
                <script>
                  (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
                  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
                  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
                  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

                  ga('create', 'UA-69101816-1', 'auto');
                  ga('send', 'pageview');
                </script>
            <style type="text/css">
                select{
                   font-family:Times;
                   font-size:16px;}
                </style>
                
        <style type="text/css">


        table{
          display:inline-block;
          margin: 0 10px;
          border-collapse: collapse;
        }
        .container{
          display:flex;
          align-items:top;
        justify-content: center;
        flex-wrap:wrap;
        }


        .inlineTable {
            display: inline-block;
            vertical-align:top
        }
        .notbold{
            font-weight:normal
        }

        .tooltip {
            position: relative;
            display: inline-block;
        }
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 340px;
            background-color: black;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px 0;
            position: absolute;
            z-index: 1;
            bottom: 110%;
            left: 50%;
            margin-left: -170px;
            margin-bottom: 10px;
        }
        .tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 100%;
            left: 50%;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: black transparent transparent transparent;
        }
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: .9;
        }
        .candidate-tooltip {
            position: relative;
            display: inline-block;
        }
        .candidate-tooltip .tooltiptext {
            visibility: hidden;
            background-color: black;
            color: #fff;
            text-align: center;
            border-radius: 6px;
            padding: 5px 0;
            position: absolute;
            z-index: 1;
            bottom: 0%;
            left: 110%;
            margin-left: -5px;
        }
        .candidate-tooltip .tooltiptext table tr td {
            color: #fff;
            font-weight: bold;
            /*
            Make the table headers will stay on one line. With this, we no
            longer have to set width on .candidate-tooltip .tooltiptext.
            (Without this, and without tooltip width, it would make the table more
            narrow and the headers would line wrap)
            */
            white-space: nowrap;
        }
        .candidate-tooltip .tooltiptext::after {
            content: "";
            position: absolute;
            top: 50%;
            left: -5px;
            margin-left: -5px;
            border-width: 5px;
            border-style: solid;
            border-color: transparent black transparent transparent;
        }
        .candidate-tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: .9;
        }

        </style>
                </head>

                <body>
                <p style="font-size: 14pt;"><b><highlight>Odds update every minute</highlight></b> | <i>Last updated: '''+str(now)+'''</i><br></p>
            <div class="centerwrap">
        <div>
            <div class="one">
        <div>
        <center><p style="font-size: 55pt; font-family:times; margin-bottom:0px; margin-top:0px"><b>Election Betting Odds</b></p></center>
                <center><p style="font-size: 20pt; font-family:times; margin-bottom:0px; margin-left:0px; margin-top:3px"><b><i>By <a href="https://www.maximumtruth.org">Maxim Lott</a> and <a href="https://twitter.com/johnstossel">John Stossel</a></i></b></p></center>
                <span style="font-size: 16pt;"><center><b><a href="/about.html">Why This Beats Polls</a> | Odds from <a href="https://www.betfair.com/exchange/plus/politics">Betfair</a>, <a href="https://smarkets.com/politics">Smarkets</a>, <a href="https://www.predictit.org/promo/electionbetting">PredictIt</a>, <a href="https://polymarket.com">Polymarket</a> | <a href="/about.html#whyBetfair">How People Bet</a></b></center></span>
               <span style="font-size: 22;"><p></span>
        '''+Nav_bar+'''
        <span style="font-size: 16;"><p></span>
            <b><span style="font-size: 16;">Hover over candidate pics to see market breakdown. Hover over underlined titles for amount bet.<br></font></span></b></center>
                <span style="font-size: 16;"><p></span></CENTER>
                
        <center><span style="font-size: 36pt;"><b><i>''' + chance_of_text + '''</i></b></span></center>
        ''' + chance_of_text_extra_html + '''
        <span style="font-size: 5;"><p></span>

        <div class="container">
        <!--...-->
                <table>
                  <TH colspan="2" scope="colgroup" bgcolor="#FFFFFF"><center><div class="tooltip"><b><u><span style="font-size: 21pt;">'''+column_title+'''</span><span class="tooltiptext">'''+race_description+'''<p>'''+total_volume_line +'''</span></div></u></b></center></TH>
        '''+rows_created + Other_bar+'''
                </table><!--...-->
        <table>
        <script type="text/javascript" src="https://www.google.com/jsapi"></script>
        <script type='text/javascript'>
        google.charts.load('current', {packages: ['line']});
        function drawChart() {
        var data = new google.visualization.DataTable();
        '''+chart_rows_created+'''

        data.addRows(['''+str(WIN_ingested_data)+str(formatted_WIN_chart_data)+''']);
        var chart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        containerId: 'WIN_chart_div',
        options: {
        height: 600,
        width: 700,
        'legend':'right',
        backgroundColor: '#FFFFFF',
        lineWidth: 4,
        '''+chart_colors+'''
        title: "'''+str(column_title.replace("<br>"," ").replace("&#x1F1FA&#x1F1E6","Ukraine").replace("&#x1F1F7&#x1F1FA","Russia"))+''' (% chance)",
        // omit width, since we set this in CSS
        chartArea: {
          width: '73%',
          top: 40,
          bottom: 200,
          left: 40,
          // this should be the same as the ChartRangeFilter
        }
        }
        });
          var view = new google.visualization.DataView(data);
          '''+chart_label_ordering+'''
          
        var control = new google.visualization.ControlWrapper({
        controlType: 'ChartRangeFilter',
        containerId: 'WIN_control_div',

        options: {
        filterColumnIndex: 0,
        ui: {
          chartOptions: {
            height: 50,
            width: 700,
            '''+chart_colors+'''
        backgroundColor: '#FFFFFF',
            
            // omit width, since we set this in CSS
            chartArea: {
              width: '73%',
              top: 0,
              left: 40,
              // this should be the same as the ChartRangeFilter
            }
          }
        }
        }
        });
        var dashboard = new google.visualization.Dashboard(document.querySelector('#dashboard_div'));
        dashboard.bind([control], [chart]);
        dashboard.draw(view);
        function zoomLastDay() {
        var range = data.getColumnRange(0);
        control.setState({
        range: {
          start: new Date(range.max.getFullYear(), range.max.getMonth(), range.max.getDate() - 1),
          end: range.max
        }
        });
        control.draw();
        }
        function zoomLastWeek() {
        var range = data.getColumnRange(0);
        control.setState({
        range: {
          start: new Date(range.max.getFullYear(), range.max.getMonth(), range.max.getDate() - 7),
          end: range.max
        }
        });
        control.draw();
        }
        function zoomLastMonth() {
        // zoom here sets the month back 1, which can have odd effects when the last month has more days than the previous month
        // eg: if the last day is March 31, then zooming last month will give a range of March 3 - March 31, as this sets the start date to February 31, which doesn't exist
        // you can tweak this to make it function differently if you want
        var range = data.getColumnRange(0);
        control.setState({
        range: {
          start: new Date(range.max.getFullYear(), range.max.getMonth() - 1, range.max.getDate()),
          end: range.max
        }
        });
        control.draw();
        }
        var runOnce = google.visualization.events.addListener(dashboard, 'ready', function() {
        google.visualization.events.removeListener(runOnce);
        if (document.addEventListener) {
        document.querySelector('#lastDay').addEventListener('click', zoomLastDay);
        document.querySelector('#lastWeek').addEventListener('click', zoomLastWeek);
        document.querySelector('#lastMonth').addEventListener('click', zoomLastMonth);
        } else if (document.attachEvent) {
        document.querySelector('#lastDay').attachEvent('onclick', zoomLastDay);
        document.querySelector('#lastWeek').attachEvent('onclick', zoomLastWeek);
        document.querySelector('#lastMonth').attachEvent('onclick', zoomLastMonth);
        } else {
        document.querySelector('#lastDay').onclick = zoomLastDay;
        document.querySelector('#lastWeek').onclick = zoomLastWeek;
        document.querySelector('#lastMonth').onclick = zoomLastMonth;
        }
        });
        }
        google.load('visualization', '1.1', {
        packages: ['controls'],
        callback: drawChart
        });
        </script>
        <style type="text/css">
        input
        {
            -webkit-border-radius: 5px; //For Safari, etc.
            -moz-border-radius: 5px; //For Mozilla, etc.
            border-radius: 5px; //CSS3 Feature
        }
        </style>
        <div id="dashboard_div">
        <br />
        <input id="lastDay" type="button" style="font-size:300%" "font: bold"  value="Last Day" />
        <input id="lastWeek" type="button" style="font-size:300%" style="font: bold"  value="Last Week" />
        <input id="lastMonth" type="button" style="font-size:300%"  value="Last Month" />
        <input id="max" type="button" style="font-size:300%" onclick="window.location.href=''" value="Maximum" />

        <select onChange="window.location.href=this.value">
        <option value="" selected>Go to another chart</option>
        '''+Chart_nav_bar+'''
        </select>

        <input id="About" type="button" style="font-size:300%" onclick="window.location.href='/chart_notes.html'" value="About" />
        <div style="margin-bottom:-70px; width:100%;" id="WIN_chart_div"></div>
        <div style="margin-top:-160px; width:100%;" id="WIN_control_div"></div>
        <a name="chart">
        </table></div>
                
            <div>
            <span style="font-size: 88;"><br></span></div>
            '''+Ad_bar+'''
            <div id="fb-root"></div>
            <script>(function(d, s, id) {
              var js, fjs = d.getElementsByTagName(s)[0];
              if (d.getElementById(id)) return;
              js = d.createElement(s); js.id = id;
              js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.5";
              fjs.parentNode.insertBefore(js, fjs);
            }(document, 'script', 'facebook-jssdk'));</script>
            <center><p style="font-size: 14pt;"><b>
            <a href="/about.html">About these odds and FAQ</a> | By <a href="http://maximlott.com">Maxim Lott</a> and <a href="http://johnstossel.com">John Stossel</a> | Odds update every minute</b></p></center>
            <center><p style="font-size: 14pt;"><b>
            <span class="fb-share-button" data-href="http://ElectionBettingOdds.com" data-layout="button_count"></span> 
             | 
            <a href="https://twitter.com/share" class="twitter-share-button" data-url="https://www.ElectionBettingOdds.com" data-text="ElectionBettingOdds.com has real-time odds about who will win the election" data-via="maximlott">Tweet</a>
            <script>!function(d,s,id){var js,fjs=d.getElementsByTagName(s)[0],p=/^http:/.test(d.location)?'http':'https';if(!d.getElementById(id)){js=d.createElement(s);js.id=id;js.src=p+'://platform.twitter.com/widgets.js';fjs.parentNode.insertBefore(js,fjs);}}(document, 'script', 'twitter-wjs');</script>
            </b></p></center>
            <center><p style="font-size: 10pt;">Copyright 2022, FTX Trading Ltd</center>
            <script type="text/javascript">
            var sc_project=10669543; 
            var sc_invisible=1; 
            var sc_security="b9af9e3a"; 
            var scJsHost = (("https:" == document.location.protocol) ?
            "https://secure." : "http://www.");
            document.write("<sc"+"ript type='text/javascript' src='" +
            scJsHost+
            "statcounter.com/counter/counter.js'></"+"script>");
            </script>
            <noscript><div class="statcounter"><a title="create counter"
            href="http://statcounter.com/free-hit-counter/"
            target="_blank"><img class="statcounter"
            src="http://c.statcounter.com/10669543/0/b9af9e3a/1/"
            alt="create counter"></a></div></noscript>
            <!-- End of StatCounter Code for Default Guide -->
            <script type="text/javascript">
            <!-- 
            var timer = setInterval("autoRefresh()", 1000 * 5 * 60);
            function autoRefresh(){self.location.reload(true);}
            //--> 
            </script>
            </div></div>
                </body>
        <span style="font-size: 20;"><p></span> 
                
                </html>''')