var dvchart=dvchart||{};dvchart["smj-pl-regression-bugs-percent"]=function(x){$.plot($(x),[{"color": "green", "data": [[1189728000000, 46.24277456647398], [1189900800000, 46.24277456647398], [1190246400000, 62.42774566473988], [1190937600000, 83.47826086956522], [1191456000000, 85.65217391304347], [1191456000000, 92.17391304347827], [1191888000000, 92.94117647058825], [1192060800000, 95.3307392996109], [1192492800000, 96.10894941634241], [1192665600000, 94.16342412451363], [1192752000000, 94.57364341085271], [1193184000000, 97.71863117870723], [1193702400000, 95.05703422053232], [1193788800000, 96.1977186311787], [1193961600000, 98.47908745247148], [1194912000000, 95.50561797752808], [1195257600000, 95.50561797752808], [1195603200000, 94.44444444444444], [1195689600000, 94.44444444444444], [1196035200000, 98.85057471264366], [1196121600000, 96.57794676806083], [1196208000000, 96.21212121212122], [1196294400000, 96.21212121212122], [1196380800000, 94.3609022556391], [1196640000000, 94.73684210526316], [1196640000000, 96.64179104477611], [1196726400000, 96.64179104477611], [1196812800000, 96.08540925266904], [1196899200000, 96.44128113879003], [1196985600000, 96.44128113879003], [1197936000000, 96.113074204947], [1198022400000, 94.77351916376307], [1198108800000, 90.42904290429043], [1199750400000, 89.50819672131148], [1199923200000, 91.14754098360655], [1200268800000, 91.80327868852459], [1200614400000, 94.27710843373495], [1201564800000, 96.07250755287009], [1201824000000, 95.23809523809524], [1204502400000, 91.28065395095368], [1207008000000, 91.32791327913279], [1210636800000, 89.15989159891599], [1212364800000, 88.26530612244898], [1222041600000, 86.25], [1222300800000, 86.25], [1223251200000, 86.0], [1224028800000, 86.0], [1224201600000, 89.75], [1224720000000, 91.0], [1226880000000, 88.99521531100478], [1227484800000, 91.62679425837321], [1228176000000, 92.36276849642005], [1228262400000, 93.30143540669857], [1228867200000, 84.89208633093524], [1229299200000, 93.5251798561151], [1229472000000, 94.7242206235012], [1229990400000, 94.7242206235012], [1233532800000, 94.74940334128878], [1241568000000, 94.13145539906102], [1254096000000, 90.57471264367815], [1256688000000, 90.57471264367815], [1257984000000, 90.57471264367815], [1262822400000, 89.68609865470852], [1273449600000, 89.23766816143498], [1282694400000, 86.09865470852019], [1286236800000, 88.56502242152466], [1290643200000, 88.36689038031321], [1291507200000, 88.74172185430463], [1295827200000, 65.71428571428571], [1296518400000, 65.71428571428571], [1296604800000, 85.49450549450549], [1299110400000, 89.91228070175438], [1299456000000, 80.7017543859649], [1299801600000, 89.52991452991454], [1304294400000, 89.85507246376812], [1305849600000, 91.7184265010352], [1306368000000, 93.46938775510205], [1308096000000, 93.46938775510205], [1314057600000, 88.28282828282828], [1314748800000, 92.54032258064517], [1315267200000, 91.93548387096774], [1315267200000, 92.54032258064517], [1315785600000, 92.49492900608519], [1316044800000, 89.47368421052632], [1316131200000, 92.10526315789474], [1316390400000, 92.51012145748989], [1316476800000, 92.51012145748989], [1316563200000, 92.51012145748989], [1316649600000, 91.95171026156942], [1316649600000, 91.95171026156942], [1318204800000, 92.0997920997921], [1318204800000, 92.0997920997921]], "label": "Solved"}, {"color": "red", "data": [[1189728000000, 54.75722543352601], [1189900800000, 54.75722543352601], [1190246400000, 38.57225433526012], [1190937600000, 17.521739130434785], [1191456000000, 8.826086956521738], [1191456000000, 15.347826086956522], [1191888000000, 8.058823529411764], [1192060800000, 5.669260700389105], [1192492800000, 4.891050583657588], [1192665600000, 6.836575875486382], [1192752000000, 6.426356589147287], [1193184000000, 3.2813688212927756], [1193702400000, 5.942965779467681], [1193788800000, 4.802281368821292], [1193961600000, 2.520912547528517], [1194912000000, 5.49438202247191], [1195257600000, 5.49438202247191], [1195603200000, 6.555555555555555], [1195689600000, 6.555555555555555], [1196035200000, 2.1494252873563218], [1196121600000, 4.422053231939163], [1196208000000, 4.787878787878788], [1196294400000, 4.787878787878788], [1196380800000, 6.639097744360901], [1196640000000, 4.35820895522388], [1196640000000, 6.263157894736842], [1196726400000, 4.35820895522388], [1196812800000, 4.91459074733096], [1196899200000, 4.5587188612099645], [1196985600000, 4.5587188612099645], [1197936000000, 4.886925795053004], [1198022400000, 6.226480836236934], [1198108800000, 10.57095709570957], [1199750400000, 11.491803278688526], [1199923200000, 9.852459016393443], [1200268800000, 9.19672131147541], [1200614400000, 6.72289156626506], [1201564800000, 4.927492447129909], [1201824000000, 5.761904761904762], [1204502400000, 9.719346049046322], [1207008000000, 9.672086720867208], [1210636800000, 11.84010840108401], [1212364800000, 12.73469387755102], [1222041600000, 14.75], [1222300800000, 14.75], [1223251200000, 15.0], [1224028800000, 15.0], [1224201600000, 11.25], [1224720000000, 10.0], [1226880000000, 12.004784688995215], [1227484800000, 9.373205741626794], [1228176000000, 8.637231503579953], [1228262400000, 7.698564593301436], [1228867200000, 16.10791366906475], [1229299200000, 7.474820143884893], [1229472000000, 6.275779376498801], [1229990400000, 6.275779376498801], [1233532800000, 6.250596658711217], [1241568000000, 6.868544600938967], [1254096000000, 10.425287356321839], [1256688000000, 10.425287356321839], [1257984000000, 10.425287356321839], [1262822400000, 11.31390134529148], [1273449600000, 11.762331838565023], [1282694400000, 14.90134529147982], [1286236800000, 12.434977578475337], [1290643200000, 12.633109619686802], [1291507200000, 12.258278145695364], [1295827200000, 35.285714285714285], [1296518400000, 35.285714285714285], [1296604800000, 15.505494505494505], [1299110400000, 11.087719298245613], [1299456000000, 20.29824561403509], [1299801600000, 11.47008547008547], [1304294400000, 11.144927536231885], [1305849600000, 9.281573498964804], [1306368000000, 7.530612244897959], [1308096000000, 7.530612244897959], [1314057600000, 12.717171717171716], [1314748800000, 8.45967741935484], [1315267200000, 8.45967741935484], [1315267200000, 9.064516129032258], [1315785600000, 8.505070993914806], [1316044800000, 11.526315789473685], [1316131200000, 8.894736842105264], [1316390400000, 8.489878542510121], [1316476800000, 8.489878542510121], [1316563200000, 8.489878542510121], [1316649600000, 9.048289738430583], [1316649600000, 9.048289738430583], [1318204800000, 8.900207900207901], [1318204800000, 8.900207900207901]], "label": "Unsolved"}],{"series": {"lines": {"fill": true, "show": true}, "stack": true}, "xaxis": {"mode": "time"}, "yaxis": {"max": 100}});};