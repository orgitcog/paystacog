<?php

defined('_JEXEC') or die('Restricted access');

class CrBcInstallation extends CrBcInstaller {

    public $type = 'payment';
    public $name = 'paystack';

        function install(){
            
            
            $tables = JFactory::getDBO()->getTableList();
            
            settype($tables, 'array');

            foreach ($tables as $table){

                if( $table == JFactory::getDBO()->getPrefix() . 'breezingcommerce_plugin_payment_paystack' ){

                    return;
                }
            }
            
            $db = JFactory::getDBO();
            $db->setQuery("CREATE TABLE IF NOT EXISTS `#__breezingcommerce_plugin_payment_paystack` (
            `identity` int(11) NOT NULL,
            `test_account` tinyint(4) NOT NULL DEFAULT '0',
            `tsk` varchar(255) NOT NULL,
            `tpk` varchar(255) NOT NULL,
            `lsk` varchar(255) NOT NULL,
            `lpk` varchar(255) NOT NULL
          ) ENGINE=InnoDB DEFAULT CHARSET=utf8
          ");
            $db->query();
        
        $db->setQuery("ALTER TABLE `#__breezingcommerce_plugin_payment_paystack`
        ADD PRIMARY KEY (`identity`)

      ");
      $db->query();

                      $db->setQuery("ALTER TABLE `#__breezingcommerce_plugin_payment_paystack`
        MODIFY `identity` int(11) NOT NULL AUTO_INCREMENT
      ");
              $db->query();
    }

}