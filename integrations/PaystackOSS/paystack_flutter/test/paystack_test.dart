import 'package:flutter_test/flutter_test.dart';
import 'package:paystack_flutter_sdk/src/models.dart';
import 'package:paystack_flutter_sdk/src/paystack_platform_interface.dart';
import 'package:paystack_flutter_sdk/src/paystack_method_channel.dart';
import 'package:plugin_platform_interface/plugin_platform_interface.dart';

class MockPaystackFlutterPlatform
    with MockPlatformInterfaceMixin
    implements PaystackSDKPlatform {
  @override
  Future<String?> getPlatformVersion() => Future.value('42');

  @override
  Future<String?> build(String publicKey, bool enableLogging) {
    return Future.value("Coming soon...");
  }
  
  @override
  Future<bool> initialize(String publicKey, bool enableLogging) {
    // TODO: implement initialize
    throw UnimplementedError();
  }

  @override
  Future<TransactionResponse> launch(String accessCode) {
    // TODO: implement launch
    throw UnimplementedError();
  }
}

void main() {
  final PaystackSDKPlatform initialPlatform =
      PaystackSDKPlatform.instance;

  test('$MethodChannelPaystackSDK is the default instance', () {
    expect(initialPlatform, isInstanceOf<MethodChannelPaystackSDK>());
  });

  test('getPlatformVersion', () async {
    // PaystackFlutter paystackFlutterPlugin = PaystackFlutter();
    MockPaystackFlutterPlatform fakePlatform = MockPaystackFlutterPlatform();
    PaystackSDKPlatform.instance = fakePlatform;

    // expect(await paystackFlutterPlugin.getPlatformVersion(), '42');
  });

  // The unit test is actually not worth it!

  test('launch', () async {
    // PaymentSheet paymentSheet = PaymentSheet();
    MockPaystackFlutterPlatform fakePlatform = MockPaystackFlutterPlatform();
    PaystackSDKPlatform.instance = fakePlatform;

    // expect(await paymentSheet.launch("accessCode"), "Launched");
  });
}
