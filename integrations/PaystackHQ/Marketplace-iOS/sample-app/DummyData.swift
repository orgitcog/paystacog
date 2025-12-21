//
//  DummyData.swift
//  sample-app
//
//  Created by James KUMAKO on 11/15/20.
//  Copyright © 2020 Kuassi Jimmy . All rights reserved.
//

import Foundation

struct Product {
  var id: Int
  var imageName: String
  var price: String
  var price_ng: Int
  var description: String
  
}


let product_list = [Product.init(id: 1, imageName: "ipad", price: "NGN 200 000",price_ng: 200000, description: "Donec sed odio dui. Nullam id dolor id nibh ultricies vehicula ut id elit."),
                    
                    Product.init(id: 1, imageName: "iphone11", price: "NGN 650 000",price_ng: 650000, description: "Cras justo odio, dapibus ac facilisis in, egestas eget quam. Vestibulum id ligula porta felis euismod semper."),
                    
                    Product.init(id: 1, imageName: "iphone12", price: "NGN 900 000",price_ng: 900000, description: "Cras mattis consectetur purus sit amet fermentum. Lorem ipsum dolor sit amet, consectetur adipiscing elit."),
                    
                    Product.init(id: 1, imageName: "macbook", price: "NGN 1 000 0000",price_ng: 1000000, description: "Donec ullamcorper nulla non metus auctor fringilla. Praesent commodo cursus magna, vel scelerisque nisl consectetur et."),
                    
                    Product.init(id: 1, imageName: "ps5", price: "NGN 400 000",price_ng: 400000, description: "Nullam id dolor id nibh ultricies vehicula ut id elit. Cras justo odio, dapibus ac facilisis in, egestas eget quam."),
                    
                    Product.init(id: 1, imageName: "xbox", price: "NGN 350 000",price_ng: 350000, description: "Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.")

                  ]


