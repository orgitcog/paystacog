<?php
session_start();
//session_save_path("./"); //path on your server where you are storing session

require("settings.php");    //file which has required settings
require("functions.php");    //file which has required functions
require("class-paystack-plugin-tracker.php");
$settings = new settings();
?>

<html>

<head>
    <title>Verifying Your Payment. Please wait...</title>
</head>

<body bgcolor="white">
    <font size=4>

        <?php
        $key = $settings->hostkey;

        $redirectUrl = $_SESSION['redirecturl'];  // redirectUrl received from foundation
        $transId = $_SESSION['transid'];         //Pass the same transid which was passsed to your Gateway URL at the beginning of the transaction.
        $sellingCurrencyAmount = $_SESSION['sellingcurrencyamount'];
        $accountingCurrencyAmount = $_SESSION['accountingcurencyamount'];
        $pstk_logger = new paystack_plugin_tracker('reseller-club', $settings->paystack_publickey);
        srand((double)microtime() * 1000000);
        $rkey = rand();

        $status = "";

        $curl = curl_init();

        curl_setopt_array($curl, array(
            CURLOPT_URL => $settings->paystack_base . "transaction/verify/" . $transId,
            CURLOPT_ENCODING => "",
            CURLOPT_MAXREDIRS => -1, //Maximum number of redirects
            CURLOPT_TIMEOUT => 0, //Timeout for request
            CURLOPT_HTTP_VERSION => CURL_HTTP_VERSION_1_1,
            CURLOPT_RETURNTRANSFER => true, //Set CURLOPT_RETURNTRANSFER so that the content is returned as a variable.
            CURLOPT_CUSTOMREQUEST => "GET",
            CURLOPT_POSTFIELDS => "",
            CURLOPT_HTTPHEADER => array(
                "Authorization: Bearer "  . $settings->paystack_secretkey,
                "Content-Type: application/json",
            )
        ));

        $response = curl_exec($curl);
        $err = curl_error($curl);

        curl_close($curl);

        if ($err) {
            echo "cURL Error #:" . $err;
        } else {
            $paymentInfo = json_decode($response);
            if ($paymentInfo->status == true) {
                if ($paymentInfo->data->status == 'success') {
                    $pstk_logger->log_transaction_success($transId);
                    $status = "Y";
                } else {
                    $status = "N";
                }
            } else {
                $status = "N";
            }
        }

        $checksum = generateChecksum($transId, $sellingCurrencyAmount, $accountingCurrencyAmount, $status, $rkey, $key);
        ?>

        <form name="f1" action="<?php echo $redirectUrl; ?>">
            <input type="hidden" name="transid" value="<?php echo $transId; ?>">
            <input type="hidden" name="status" value="<?php echo $status; ?>">
            <input type="hidden" name="rkey" value="<?php echo $rkey; ?>">
            <input type="hidden" name="checksum" value="<?php echo $checksum; ?>">
            <input type="hidden" name="sellingamount" value="<?php echo $sellingCurrencyAmount; ?>">
            <input type="hidden" name="accountingamount" value="<?php echo $accountingCurrencyAmount; ?>">
        </form>

        <?php echo "<script>document.f1.submit();</script>"; ?>
    </font>
</body>

</html>