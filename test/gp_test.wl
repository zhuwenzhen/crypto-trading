(* ::Package:: *)

(* ::Title:: *)
(*Gaussian Process Model Evaluation*)


(* ::Section:: *)
(*1. Import pre-trained models*)


dir = "/home/wenzhenz/CryptoTrading/";
p1 = Import[dir <> "model/p1.wxf"];
p2 = Import[dir <> "model/p2.wxf"];
p3 = Import[dir <> "model/p3.wxf"];
gp = Import[dir <> "model/GP.wxf"];


(* ::Section:: *)
(*2. Query input from database*)


Needs["DatabaseLink`"];
conn = OpenSQLConnection[JDBC["MySQL(Connector/J)", "localhost/crypto"], "Username" -> "xxx", "Password" -> ""];


(* ::Section:: *)
(*3. Evaluate on model*)


$idIndex = 1;
$timeIndex = 2;
$priceIndex = 3;
$bidIndex = 4;
$askIndex = 5;
$predictPriceGPIndex = 6;
$LBIndex = 7;
$UBIndex = 8;


gpUpperBound[x_]:= gp[x] + StandardDeviation[gp[x, "Distribution"]]
gpLowerBound[x_]:= gp[x] - StandardDeviation[gp[x, "Distribution"]]

\[Gamma][{Vbid_, Vask_}]:= (Vbid - Vask)/(Vbid + Vask)


computeDeltaP[conn_]:= Module[
	{sqlCmd, data, gamma, input, inputForP1, inputForP2, inputForP3, 
	dp1, dp2, dp3, dp, price, sqlWrite, id, upperBound, lowerBound,
	sqlGP, sqlUB, sqlLB},
	(* Query the testing data from database *)
	sqlCmd = "SELECT * FROM (SELECT * FROM btc_btc ORDER BY id DESC LIMIT 721) as r ORDER BY id";
	data = SQLExecute[conn, sqlCmd];
	input = data[[All, $priceIndex ;; $askIndex]];
	id = data[[-1, $idIndex]];
	
	(* Organize input data *)
	inputForP1 = input[[-180 ;; All]];
	inputForP2 = input[[-360 ;; All]];
	inputForP3 = input[[-720 ;; All]];
	
	price = input[[-1, 1]];
	
	(* Compute deltaP model 1, 2, 3 and gamma*)
	dp1 = p1[inputForP1];
	dp2 = p2[inputForP2];
	dp3 = p3[inputForP3];
	gamma = \[Gamma][input[[-1, -2 ;; -1]]];
	
	(*Compute final delta P (price change) and upperbound / lowerbound*)
	
	dp = gp[{dp1, dp2, dp3, gamma}];
	Print[dp];
	lowerBound = gpLowerBound[{dp1, dp2, dp3, gamma}];
	upperBound = gpUpperBound[{dp1, dp2, dp3, gamma}];
	
	(* Prepare SQL queries *)
	sqlGP = "UPDATE btc_btc SET predict_price_GP = " <> ToString[dp + price] <> " WHERE id = " <> ToString[id];
	sqlUB = "UPDATE btc_btc SET GP_UB = " <> ToString[upperBound + price] <> " WHERE id = " <> ToString[id];
	sqlLB = "UPDATE btc_btc SET GP_LB = " <> ToString[lowerBound + price] <> " WHERE id = " <> ToString[id];
	
	(* Update database *)
	SQLExecute[conn, sqlGP];
	SQLExecute[conn, sqlUB];
	SQLExecute[conn, sqlLB];
	
	Print[dp + price, ", lowerbound: ", lowerBound + price, ", upperbound:", upperBound + price];
	dp
]


While[True, computeDeltaP[conn]; Pause[10]]
(*computeDeltaP[conn];*)
