import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:developer';

import 'package:paystack_flutter_sdk/paystack_flutter_sdk.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  String _reference = "";
  final _publicKey = "pk_test_xxxxxx";
  final _accessCode = "2ksqdeqqlbpqg24";
  final _paystack = Paystack();

  @override
  void initState() {
    super.initState();
    initialize(_publicKey);
  }

  initialize(String publicKey) async {
        try {
      final response = await _paystack.initialize(publicKey, true);
      if (response) {
        log("Sucessfully initialised the SDK");
      } else {
        log("Unable to initialise the SDK");
      }
    } on PlatformException catch (e) {
      log(e.message!);
    }
  }

  launch() async {
    String reference = "";
    try {
      final response = await _paystack.launch(_accessCode);
      if (response.status == "success") {
        reference = response.reference;
        log(reference);
      } else if(response.status == "cancelled") {
        log(response.message);
      } else {
        log(response.message);
      }
    } on PlatformException catch (e) {
      log(e.message!);
    }

    setState(() {
      _reference = reference;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
          appBar: AppBar(
            title: const Text('Paystack SDK'),
          ),
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                    onPressed: launch, child: const Text('Make Payment')),
                Text(
                  "Ref: $_reference",
                  style: Theme.of(context).textTheme.bodyMedium,
                )
              ],
            ),
          ),
          )
    );
  }
}
