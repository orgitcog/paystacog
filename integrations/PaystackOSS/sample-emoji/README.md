# sample-emoji
A SwiftUI sample app showing Paystack's new iOS SDK. The new SDK requires a transaction to be [Initialized on Paystack](https://paystack.com/docs/api/transaction/#initialize) via your backend and completed using your ``public_api_key`` and ``access_code`` on the app.

## Getting Started
To install the SDK using [Swift Package Manager](https://github.com/apple/swift-package-manager) you can follow the [Apple developer guide here](https://developer.apple.com/documentation/xcode/adding_package_dependencies_to_your_app) and enter the url *https://github.com/PaystackHQ/paystack-sdk-ios.git*.

After installing SDK, import it using:
```swift
import PaystackCore
import PaystackUI
```

Initialize the Paystack object using your public key from your Paystack dashboard:
```swift
let paystackObject = try? PaystackBuilder
            .newInstance
            .setKey("pk_test_your_public_key")
            .build()
```

The SDK contains a custom button you can use to launch the transaction
```swift
paystackObject?.chargeUIButton(accessCode: "your-access-code", onComplete: paymentDone) {
                    // Stylize your button
                    Text("Buy Emoji")
                }
```
The ``accessCode`` value is returned from the Transaction Initialize endpoint, by your server.

Incase you need any help, please reach out to [techsupport@paystack.com](mailto:techsupport@paystack.com). 

