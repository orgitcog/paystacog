//
//  DetailViewController.swift
//  sample-app
//
//  Created by James KUMAKO on 11/15/20.
//  Copyright © 2020 Kuassi Jimmy . All rights reserved.
//

import UIKit
import Paystack

class DetailViewController: UIViewController {

  
  
  var product: Product!
  
  @IBOutlet weak var imageView: UIImageView?
  @IBOutlet weak var price: UILabel?
  @IBOutlet weak var details: UILabel?
  @IBOutlet weak var buy: UIButton?
  
  override func viewDidLoad() {
    super.viewDidLoad()
    self.imageView?.image = UIImage.init(named: product.imageName)
    self.details?.text = product.description
    self.price?.text = product.price
    
      
  }
  
 
  // MARK: - Navigation
   
  override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    if segue.identifier == "payVC" {
      let vc = segue.destination as! PaymentViewController
      vc.product = self.product
    }
  }
  
   
}
