<?php

defined('_JEXEC') or die('Restricted access');
?>
<script type="text/javascript">
    function submitbutton(pressbutton) {
	submitform(pressbutton);
    }
    /**
    * Submit the admin form
    */
    function submitform(pressbutton){
            if (pressbutton) {
                    document.adminForm.task.value=pressbutton;
            }
            if (typeof document.adminForm.onsubmit == "function") {
                    document.adminForm.onsubmit();
            }
            document.adminForm.submit();
    }

    function crbc_submitbutton(pressbutton)
    {
        switch (pressbutton) {
            case 'plugin_cancel':
                pressbutton = 'cancel';
                submitform(pressbutton);
                break;
            case 'plugin_apply':
                var error = false;

                if(!error)
                {
                    submitform(pressbutton);
                }

                break;
        }
    }

    // Joomla 1.6 compat
    if(typeof Joomla != 'undefined'){
        Joomla.submitbutton = crbc_submitbutton;
    }
    // Joomla 1.5 compat
    submitbutton = crbc_submitbutton;
</script>

<div class="form-horizontal">
     <div class="control-group">
        <div class="control-label">
            <label for="test_account" class="tip-top hasTooltip" title="<?php echo JHtml::tooltipText( 'COM_BREEZINGCOMMERCE_PAYSTACK_TESTACC_TIP' ); ?>"><?php echo JText::_( 'COM_BREEZINGCOMMERCE_PAYSTACK_TESTACC' ); ?></label>
        </div>
        <div class="controls">
            <input type="checkbox" name="test_account" id="test_account" value="1"<?php echo $this->entity->test_account == 1 ? ' checked="checked"' : ''; ?>/>
        </div>
    </div>

    <div class="control-group">
        <div class="control-label">
            <label for="tsk" class="tip-top hasTooltip"><?php echo JText::_( 'COM_BREEZINGCOMMERCE_PAYSTACK_TSK' ); ?></label>
        </div>
        <div class="controls">
            <input type="text" name="tsk" id="tsk" value="<?php echo $this->escape( $this->entity->tsk); ?>"/>
        </div>
    </div>

     <div class="control-group">
        <div class="control-label">
            <label for="tpk" class="tip-top hasTooltip"><?php echo JText::_( 'COM_BREEZINGCOMMERCE_PAYSTACK_TPK' ); ?></label>
        </div>
        <div class="controls">
            <input type="text" name="tpk" id="tpk" value="<?php echo $this->escape( $this->entity->tpk); ?>"/>
        </div>
    </div>
     <div class="control-group">
        <div class="control-label">
            <label for="lsk" class="tip-top hasTooltip"><?php echo JText::_( 'COM_BREEZINGCOMMERCE_PAYSTACK_LSK' ); ?></label>
        </div>
        <div class="controls">
            <input type="text" name="lsk" id="lsk" value="<?php echo $this->escape( $this->entity->lsk); ?>"/>
        </div>
    </div>

     <div class="control-group">
        <div class="control-label">
            <label for="lpk" class="tip-top hasTooltip"><?php echo JText::_( 'COM_BREEZINGCOMMERCE_PAYSTACK_LPK' ); ?></label>
        </div>
        <div class="controls">
            <input type="text" name="lpk" id="lpk" value="<?php echo $this->escape( $this->entity->lpk); ?>"/>
        </div>
    </div>

</div>

<input type="hidden" name="identity" value="<?php echo $this->entity->identity;?>"/>
