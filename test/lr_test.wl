(* ::Package:: *)

(* ::Title:: *)
(*Model Evaluation*)


dir = "/home/wenzhenz/CryptoTrading/";


(* ::Text:: *)
(*Import pre-trained models:*)


p1 = Import[dir <> "model/p1.wxf"];
p2 = Import[dir <> "model/p2.wxf"];
p3 = Import[dir <> "model/p3.wxf"];
\[Delta]P = Import[dir <> "model/pFinal.wxf"];


(* ::Text:: *)
(*Get input from database*)


Needs["DatabaseLink`"]
conn = OpenSQLConnection[JDBC["MySQL(Connector/J)", "localhost/crypto"], "Username" -> "root", "Password" -> ""];
\[Gamma][{Vbid_, Vask_}]:= (Vbid - Vask)/(Vbid + Vask)


$idIndex = 1;
$timeIndex = 2;
$priceIndex = 3;
$bidIndex = 4;
$askIndex = 5;
$predictPriceLRIndex = 6;


computeDeltaP[conn_]:= Module[
	{sqlCmd, data, gamma, input, inputForP1, inputForP2, inputForP3, dp1, dp2, dp3, dp, price, sqlWrite, id, sql},
	sqlCmd = "SELECT * FROM (SELECT * FROM btc_btc ORDER BY id DESC LIMIT 721) as r ORDER BY id";
	data = SQLExecute[conn, sqlCmd];
	input = data[[All, $priceIndex;;$askIndex]];
	id = data[[-1, $idIndex]];
	gamma = \[Gamma][input[[-1, -2 ;; -1]]];
	inputForP1 = input[[-180 ;; All]];
	inputForP2 = input[[-360 ;; All]];
	inputForP3 = input[[-720 ;; All]];
	price = input[[-1, 1]];
	dp1 = p1[inputForP1];
	dp2 = p2[inputForP2];
	dp3 = p3[inputForP3];
	dp = \[Delta]P[{dp1, dp2, dp3, gamma}];
	sqlWrite = "UPDATE btc_btc SET predict_price_LR = " <> ToString[dp + price - 20] <> " WHERE id = " <> ToString[id];
	sql = SQLExecute[conn, sqlWrite];
	Print[dp + price - 20];
	dp
]


While[True, computeDeltaP[conn]; Pause[10]];

CloseSQLConnection[conn]
