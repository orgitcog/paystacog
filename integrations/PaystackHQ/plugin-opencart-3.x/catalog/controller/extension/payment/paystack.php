<?php
class open_cart_paystack_plugin_tracker
{
    var $public_key;
    var $plugin_name;
    function __construct($plugin, $pk)
    {
        //configure plugin name
        //configure public key
        $this->plugin_name = $plugin;
        $this->public_key = $pk;
    }



    function log_transaction_success($trx_ref)
    {
        //send reference to logger along with plugin name and public key
        $url = "https://plugin-tracker.paystackintegrations.com/log/charge_success";

        $fields = [
            'plugin_name'  => $this->plugin_name,
            'transaction_reference' => $trx_ref,
            'public_key' => $this->public_key
        ];

        $fields_string = http_build_query($fields);

        $ch = curl_init();

        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $fields_string);

        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

        //execute post
        $result = curl_exec($ch);
        //  echo $result;
    }
}


class ControllerExtensionPaymentPaystack extends Controller
{
    public function index()
    {
        $this->load->model('checkout/order');

        $this->load->language('extension/payment/paystack');

        $data['button_confirm'] = $this->language->get('button_confirm');

        $data['text_testmode'] = $this->language->get('text_testmode');
        $data['livemode'] = $this->config->get('payment_paystack_live');

        if ($this->config->get('payment_paystack_live')) {
            $data['key'] = $this->config->get('payment_paystack_live_public');
        } else {
            $data['key'] = $this->config->get('payment_paystack_test_public');
        }

        $order_info = $this->model_checkout_order->getOrder($this->session->data['order_id']);

        $data['currency'] = $order_info['currency_code'];
        $data['ref']      = uniqid('' . $this->session->data['order_id'] . '-');
        $data['amount']   = intval($this->currency->format($order_info['total'] * 100, $order_info['currency_code'], $order_info['currency_value'], false));
        $data['email']    = $order_info['email'];
        $data['callback'] = $this->url->link('extension/payment/paystack/callback', 'trxref=' . rawurlencode($data['ref']), 'SSL');

        return $this->load->view('extension/payment/paystack', $data);
    }

    private function query_api_transaction_verify($reference)
    {
        if ($this->config->get('payment_paystack_live')) {
            $skey = $this->config->get('payment_paystack_live_secret');
        } else {
            $skey = $this->config->get('payment_paystack_test_secret');
        }

        $context = stream_context_create(
            array(
                'http' => array(
                    'method' => "GET",
                    'header' => "Authorization: Bearer " .  $skey,
                    'user-agent' => "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
                )
            )
        );
        $url = 'https://api.paystack.co/transaction/verify/' . rawurlencode($reference);
        $request = file_get_contents($url, false, $context);
        return json_decode($request, true);
    }

    private function redir_and_die($url, $onlymeta = false)
    {
        if (!headers_sent() && !$onlymeta) {
            header('Location: ' . $url);
        }
        echo "<meta http-equiv=\"refresh\" content=\"0;url=" . addslashes($url) . "\" />";
        die();
    }

    public function callback()
    {
        if (isset($this->request->get['trxref'])) {
            $trxref = $this->request->get['trxref'];

            // order id is what comes before the first dash in trxref
            $order_id = substr($trxref, 0, strpos($trxref, '-'));
            // if no dash were in transation reference, we will have an empty order_id
            if (!$order_id) {
                $order_id = 0;
            }

            $this->load->model('checkout/order');

            $order_info = $this->model_checkout_order->getOrder($order_id);

            if ($order_info) {
                if ($this->config->get('payment_paystack_debug')) {
                    $this->log->write('PAYSTACK :: CALLBACK DATA: ' . print_r($this->request->get, true));
                }

                // Callback paystack to get real transaction status
                $ps_api_response = $this->query_api_transaction_verify($trxref);

                $order_status_id = $this->config->get('config_order_status_id');

                if (array_key_exists('data', $ps_api_response) && array_key_exists('status', $ps_api_response['data']) && ($ps_api_response['data']['status'] === 'success')) {
                    //PSTK Logger 
                    if ($this->config->get('payment_paystack_live')) {
                        $pk = $this->config->get('payment_paystack_live_public');
                    } else {
                        $pk = $this->config->get('payment_paystack_test_public');
                    }

                    $pstk_logger = new open_cart_paystack_plugin_tracker('opencart-3.x', $pk);
                    $pstk_logger->log_transaction_success($trxref);

                    //----------------------
                    $order_status_id = $this->config->get('payment_paystack_order_status_id');
                    $redir_url = $this->url->link('checkout/success');
                } elseif (array_key_exists('data', $ps_api_response) && array_key_exists('status', $ps_api_response['data']) && ($ps_api_response['data']['status'] === 'failed')) {
                    $order_status_id = $this->config->get('payment_paystack_declined_status_id');
                    $redir_url = $this->url->link('checkout/checkout', '', 'SSL');
                } else {
                    $order_status_id = $this->config->get('payment_paystack_canceled_status_id');
                    $redir_url = $this->url->link('checkout/checkout', '', 'SSL');
                }

                $this->model_checkout_order->addOrderHistory($order_id, $order_status_id);
                $this->redir_and_die($redir_url);
            }
        } else if ((strtoupper($_SERVER['REQUEST_METHOD']) == 'POST') && array_key_exists('x-paystack-signature', $_SERVER)) { // WEBHOOK CODE

            // Retrieve the request's body
            $input = @file_get_contents("php://input");

            if ($this->config->get('payment_paystack_live')) {
                $secret_key = $this->config->get('payment_paystack_live_secret');
            } else {
                $secret_key = $this->config->get('payment_paystack_test_secret');
            }

            // validate event do all at once to avoid timing attack
            if ($_SERVER['HTTP_X_PAYSTACK_SIGNATURE'] !== hash_hmac('sha512', $input, $secret_key))
                exit();

            http_response_code(200);

            // parse event (which is json string) as object
            // Do something - that will not take long - with $event
            $event = json_decode($input);

            if ($event['event'] == 'charge.success') {

                $trxref = $event['data']['reference'];

                // order id is what comes before the first dash in trxref
                $order_id = substr($trxref, 0, strpos($trxref, '-'));
                // if no dash were in transation reference, we will have an empty order_id
                if (!$order_id) {
                    $order_id = 0;
                }

                $this->load->model('checkout/order');

                $order_info = $this->model_checkout_order->getOrder($order_id);

                $order_status_id = $this->config->get('config_order_status_id');

                if (array_key_exists('data', $event) && array_key_exists('status', $event['data']) && ($event['data']['status'] === 'success')) {
                    //PSTK Logger 
                    if ($this->config->get('payment_paystack_live')) {
                        $pk = $this->config->get('payment_paystack_live_public');
                    } else {
                        $pk = $this->config->get('payment_paystack_test_public');
                    }

                    $pstk_logger = new open_cart_paystack_plugin_tracker('opencart-3.x', $pk);
                    $pstk_logger->log_transaction_success($trxref);

                    //----------------------
                    $order_status_id = $this->config->get('payment_paystack_order_status_id');
                } elseif (array_key_exists('data', $event) && array_key_exists('status', $event['data']) && ($event['data']['status'] === 'failed')) {
                    $order_status_id = $this->config->get('payment_paystack_declined_status_id');
                } else {
                    $order_status_id = $this->config->get('payment_paystack_canceled_status_id');
                }

                $this->model_checkout_order->addOrderHistory($order_id, $order_status_id);
            }
            exit();
        }
    }
}
