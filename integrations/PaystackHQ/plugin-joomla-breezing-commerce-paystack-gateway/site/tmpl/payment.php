<?php

defined('_JEXEC') or die('Restricted access');

$key = $paystack->lpk;
if ($paystack->test_account == 1) {
   $key = $paystack->tpk;
}

$html = '<div class="crbc-poster hero-unit"><div>'.JText::_('Loading Paystack...').'</div>
<br>
<form>
  <script src="https://js.paystack.co/v1/inline.js"></script>
  <button type="button" class="crbc-btn btn btn-primary text-center btn-lg" onclick="payWithPaystack()" style="font-size:30px;padding: 15px;color:#fff"> Pay Now</button>
</form>

</div>';

echo $html;

?>


 
<script>
  function payWithPaystack(){
    var handler = PaystackPop.setup({
      key: '<?php echo $key; ?>',
      email: '<?php echo $paystack->email; ?>',
      amount: '<?php echo $paystack->total; ?>',
      ref: "<?php echo $paystack->reference; ?>",
      currency:"<?php echo strtoupper($paystack->currency); ?>",
      callback: function(response){
         window.location = "<?php echo $paystack->return_url; ?>";
      },
      onClose: function(){
          alert('Are you sure you want to cancel? ');
      }
    });
    handler.openIframe();
  }
  payWithPaystack();

</script>