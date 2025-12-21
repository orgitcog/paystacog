//
//  ContentView.swift
//  sample-emoji
//
//  Created by Andrew Nduati on 05/12/2023.
//

import SwiftUI
import PaystackCore
import PaystackUI

enum Emoji: String, CaseIterable {
    case 😀, 🎉, 🤪, 🇰🇪
}

struct ContentView: View {
   @State var selection: Emoji = .🎉
    let paystackObject = try? PaystackBuilder
            .newInstance
            .setKey("pk_test_your_public_key")
            .build()
    var body: some View {
        NavigationView {
            VStack {
                Text(selection.rawValue)
                    .font(.system(size: 150))
                
                Picker("Select Emoji", selection: $selection) {
                    ForEach(Emoji.allCases, id: \.self) { emoji in
                        Text(emoji.rawValue)
                    }
                }
                .pickerStyle(.segmented)
                
                // Access code is returned from the Transaction Initialize endpoint.
                paystackObject?.chargeUIButton(accessCode: "yk9dbhz1u71hcv7", onComplete: paymentDone) {
                    // Stylize your button
                    Text("Buy Emoji")
                }
            }
            .navigationTitle("Emoji Store")
            .padding()
        }
        
    }
    func paymentDone(result: TransactionResult) {
      // Handle transaction result
        print(result)
    }
}

#Preview {
    ContentView()
}
