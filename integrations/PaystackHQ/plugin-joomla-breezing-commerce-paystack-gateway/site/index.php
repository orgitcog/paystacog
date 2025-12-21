<?php

defined('_JEXEC') or die('Restricted access');

$libpath = JPATH_ADMINISTRATOR . DS . 'components' . DS . 'com_breezingcommerce' . DS . 'classes' . DS . 'plugin' . DS;
require_once($libpath . 'CrBcAPaymentSitePlugin.php');
require_once($libpath . 'CrBcPaymentSitePlugin.php');

class CrBc_Plugins_Payment_Paystack_Site extends CrBcAPaymentSitePlugin implements CrBcPaymentSitePlugin
{
    private $tx = '';
    
    function __construct() {
        // always call the parent constructor and always call it _first_
        parent::__construct();
        // define the default table for built-in list/details view
        $this->table = '#__breezingcommerce_plugin_payment_paystack';
    }
    
    /**
     * Will return the tx id and is called right after a successfull and verified payment
     * through $this->verifyPayment()
     * 
     * @return mixed
     */
    function getPaymentTransactionId(){
        
        return $this->tx;
    }

    function verifyTransaction($paystack,$reference)
    {
        $key = $paystack->lsk;
        if ($paystack->test_account == 1) {
           $key = $paystack->tsk;
        }

        $url = 'https://api.paystack.co/transaction/verify/' . $reference;

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
        curl_setopt(
            $ch, CURLOPT_HTTPHEADER, [
                'Authorization: Bearer ' . $key]
        );
        $request = curl_exec($ch);
        curl_close($ch);

        if ($request) {
            $result = json_decode($request, false);
        }
        if ($result->data->status == "success") {
            $paid = $result->data->amount / 100;
            $result = ['result' => 'success', 'amount' => $paid,'response' => $result->data->gateway_response];

        } else {
            $result = ['result' => 'failed'];

        }
        return $result;
    }
    
   
   
    function verifyPayment(CrBcCart $_cart, stdClass $order){

        $db = JFactory::getDBO();
        
        $db->setQuery("Select * From " . $this->table . " Order By `".$this->identity_column."` Desc Limit 1");
        $paystack = $db->loadObject();

        if(!($paystack instanceof stdClass)){
            throw new Exception('No paystack payment setup found, please create one first in Admin => BreezingCommerce => Plugins => Paystack');
        }
        
        if($order === null || $_cart === null){
            throw new Exception('Invalid order object');
        }
        
        $_cart_items = $_cart->getItems(true);
        
        if(count($_cart_items) == 0){
            throw new Exception('Empty cart');
        }
        
        $db->setQuery("Select * From #__breezingcommerce_plugins Where published = 1 And type = 'shipping' Order By `ordering`");
        $shipping_plugins = $db->loadAssocList();
        
        $data = CrBcCart::getData($order->id, $_cart_items, -1, -1);
        
        
        $_order_info = CrBcCart::getOrder(
                                    $order->id, 
                                    $_cart, 
                                    $_cart->getArray(), 
                                    $_cart_items, 
                                    $order->customer_id,
                                    $data,
                                    $shipping_plugins,
                                    array()
                            );


        $reference = $_GET['reference'];
        $order_details  = explode( '_',$reference);

        $order_id       = (int) $order_details[0];
        if ($order_id != $order->id) {
              throw new Exception('Transaction Reference not linked to order');
        }

        $result =  $this->verifyTransaction($paystack,$reference);

        if ($result['result'] == 'success') {
            if ($_order_info->grand_total != $result['amount']) {
                  throw new Exception('Transaction Reference not linked to order');
            }else{
                return true;
            }
        }else{
              throw new Exception('Transaction not successful');

        }
        
        return false;
    }
    
    function getInitOutput(){
        
        $db = JFactory::getDBO();
        
        require_once(JPATH_COMPONENT_ADMINISTRATOR.DS.'classes'.DS.'CrBcCart.php');
        
        $_session_cart = JFactory::getSession()->get('crbc_cart', array());
        
        if(!isset($_session_cart['checkout']) || !isset($_session_cart['checkout']['payment_plugin_id'])){
            throw new Exception('User checkout not performed yet');
        }
        
        $payment_plugin_id = intval($_session_cart['checkout']['payment_plugin_id']);
        
        $_cart = new CrBcCart( $_session_cart );
        print_r($cart);
        $_cart_items = $_cart->getItems(true);
        
        if(count($_cart_items) == 0){
            
            throw new Exception('Trying to pay an empty cart');
        }
        
        $db->setQuery("Select * From #__breezingcommerce_plugins Where published = 1 And type = 'shipping' Order By `ordering`");
        $shipping_plugins = $db->loadAssocList();
        
        $data = CrBcCart::getData($_session_cart['order_id'], $_cart_items, -1, -1);
        
        $_order_info = CrBcCart::getOrder(
                                    $_session_cart['order_id'], 
                                    $_cart, 
                                    $_session_cart, 
                                    $_cart_items, 
                                    $_session_cart['customer_id'],
                                    $data,
                                    $shipping_plugins,
                                    array()
                            );
        
        if($_order_info->grand_total <= 0){
            
            throw new Exception('Trying to use paystack while the total is zero.');
        }
        
        $db->setQuery("Select * From " . $this->table . " Order By `".$this->identity_column."` Desc Limit 1");
        $paystack = $db->loadObject();

        if(!($paystack instanceof stdClass)){
            throw new Exception('No paystack payment setup found, please create one first in Admin => BreezingCommerce => Plugins => Paystack');
        }
        
        
       
        $paystack->url = '';
        //$paystack->item_number = 0;
        //$business_name = CrBcHelpers::getBcConfig()->get('business_name', 'Default Shop Name');
        //$paystack->item_name = JText::_('Your order at') . ' ' . $business_name;
        //$paystack->amount = $_order_info->price_net;
        
        $paystack->items = $_cart_items;
        
        $paystack->tax = $_order_info->taxes;
        $paystack->locale = JFactory::getApplication()->getLanguage()->getTag();
        $paystack->locale = explode('-',$paystack->locale);
        $paystack->locale = $paystack->locale[1];
        
        if( $paystack->force_locale != '' ){
            
            $paystack->locale = $paystack->force_locale;
        }
        
        $paystack->currency = $_cart->currency_code;
        
        if( $paystack->force_currency != '' ){
            
            $paystack->currency = $paystack->force_currency;
        }
        $customer_id = $_session_cart['checkout']['userid'];
        $paystack->email =  $_order_info->customer->email;
        $paystack->total =  $_order_info->grand_total * 100;
        
        if($paystack->cancel_url == ''){
           $paystack->cancel_url = JUri::root().'media/breezingcommerce/plugins/payment/paystack/site/paystack.png'; 
        }
        
        $paystack->no_shipping = $_cart->isVirtualOrder($_cart_items) ? 1 : 0;
        
        $paystack->shipping = $_order_info->shipping_costs;
        
        $paystack->order_id = $_session_cart['order_id'];
        
        $paystack->payment_plugin_id = $payment_plugin_id;
        $paystack->reference = $paystack->order_id.'_'.time();

        
        $paystack->return_url = JUri::getInstance()->toString().'&order_id='.$paystack->order_id.'&reference='.$paystack->reference.'&verify_payment=1&payment_plugin_id='.$paystack->payment_plugin_id;
        
        ob_start();
        require_once( JPATH_SITE . '/media/breezingcommerce/plugins/payment/paystack/site/tmpl/payment.php' );
        $content = ob_get_contents();
        ob_end_clean();
        
        return $content;
    }
    
    /**
     * Optional method to prevent this payment from being used if it's not suitable.
     * For example determing if user's location is actually suitable for the payment option.
     * If it returns false, the option won't be displayed upon checkout and also not being processed.
     * 
     * @return boolean
     */
    function isPaymentSuitable(){
        return true;
    }
    
    function getAfterPaymentInfo(){
        return JText::_('COM_BREEZINGCOMMERCE_PAYSTACK_INFO_PAID');
    }
    
    public function getPluginDisplayName(){
        return JText::_('COM_BREEZINGCOMMERCE_PAYSTACK');
    }
    
    public function getPluginIcon(){
        $img = JUri::root().'media/breezingcommerce/plugins/payment/paystack/site/paystack.png';
        return '<img src="'.$img.'" width="250px">';
    }
    
    public function getPluginDescription(){
        return JText::_('COM_BREEZINGCOMMERCE_PAYSTACK_DESCRIPTION');
    }
    
    function getPaymentInfo(){
        $db = JFactory::getDBO();

        $db->setQuery("Select * From " . $this->table . " Order By `".$this->identity_column."` Desc Limit 1");
        $row = $db->loadObject();

        if(!($row instanceof stdClass)){
            $row = new stdClass();
            $row->info = JText::_('No payment info available');
        }
        
        $id = $this->identity_column;
        
        $result = CrBcHelpers::loadTranslation($row->$id, 'plugin_payment_paystack');
        
        if($result){
            
            $row->info = $result->body;
        }
        
        return $row->info;
    }
}