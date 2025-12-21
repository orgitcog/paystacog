//
//  FirstViewController.swift
//  sample-app
//
//  Created by Kuassi Jimmy  on 10/02/2020.
//  Copyright © 2020 Kuassi Jimmy . All rights reserved.
//

import UIKit

class FirstViewController: UIViewController {
  
  var selectedProduct : Product!

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
    }
  
  override func prepare(for segue: UIStoryboardSegue, sender: Any?) {
    if segue.identifier == "detailVC" {
      let vc = segue.destination as! DetailViewController
      vc.product = self.selectedProduct
    }
  }


}

extension FirstViewController: UICollectionViewDelegateFlowLayout,UICollectionViewDelegate, UICollectionViewDataSource {
  
  func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
    
      return product_list.count
  }
  
  func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
    let cell = collectionView.dequeueReusableCell(withReuseIdentifier: "cellView", for: indexPath) as! CollectionViewCell
    cell.imageView?.image = UIImage.init(named: product_list[indexPath.row].imageName)
    cell.price?.text = "NGN " + product_list[indexPath.row].price
    
    return cell
  }
  
  func collectionView(_ collectionView: UICollectionView, layout collectionViewLayout: UICollectionViewLayout, sizeForItemAt indexPath: IndexPath) -> CGSize {
    
    
    let screenWidth = UIScreen.main.bounds.width
    
    return CGSize(width: screenWidth/2 - 2 ,height: 240)
  }
  
  
  func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
    selectedProduct =  product_list[indexPath.row]
    self.performSegue(withIdentifier: "detailVC", sender: self)
  }
}

