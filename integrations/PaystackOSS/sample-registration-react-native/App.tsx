import React from 'react';
import {
  StyleSheet,
  Text,
  TextInput,
  View,
  SafeAreaView,
  Button,
  NativeModules,
} from 'react-native';
import RadioGroup from 'react-native-radio-buttons-group';
import Snackbar from 'react-native-snackbar';
import 'react-native-url-polyfill/auto';
import {createClient} from '@supabase/supabase-js';
import {SUPABASE_URL, SUPABASE_KEY} from '@env';

function App(): JSX.Element {
  const {PaystackModule} = NativeModules;
  const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
  const [transactionReference, setTransactionReference] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [quantity, setQuantity] = React.useState('');
  const [tickets, setTickets] = React.useState([]);
  const [pricelist, setPricelist] = React.useState({});
  const [total, setTotal] = React.useState(0);
  const [selectedTicket, setSelectedTicket] = React.useState('');

  const getTickets = async () => {
    const {data, error} = await supabase.functions.invoke('fetch-tickets');

    if (data) {
      parseResponse(data.data);
    }

    if (error) {
      console.log('Error: ', error);
    }
  };

  React.useEffect(() => {
    getTickets();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const parseResponse = (json: any[]) => {
    // @ts-ignore
    const result = [];
    const price = {};
    json.forEach(ticket => {
      result.push({
        id: ticket.id,
        label: ticket.name,
        value: ticket.id,
      });
      // @ts-ignore
      price[ticket.id] = ticket.price;
    });

    // @ts-ignore
    setTickets(result);
    setPricelist(price);
  };

  const updateTotal = (value: string) => {
    // @ts-ignore
    setTotal(parseInt(value, 10) * pricelist[selectedTicket]);
    setQuantity(value);
  };

  const updateSelectedTicket = (value: string) => {
    if (!quantity && quantity.length < 1) {
      setQuantity('0');
    }
    //@ts-ignore
    setTotal(parseInt(quantity, 10) * pricelist[value]);
    setSelectedTicket(value);
  };

  const resetState = () => {
    setEmail('');
    setQuantity('0');
    setSelectedTicket('');
    setTotal(0);
  };

  const submitForm = () => {
    // mutiply total by 100
    PaystackModule.makePayment(total * 100, (ref: string) => {
      console.log('transaction ref: ', ref);
      setTransactionReference(transactionReference);
      // confirm payment, then do post payment activiteis
      completeRegistration();
    });
  };

  const completeRegistration = async () => {
    const {data, error} = await supabase.functions.invoke(
      'create-registration',
      {
        body: {
          email: email,
          quantity: quantity,
          ticket_id: selectedTicket,
        },
      },
    );

    if (data) {
      Snackbar.show({
        text: 'Registration successful!',
        duration: Snackbar.LENGTH_SHORT,
      });
      resetState();
    }

    if (error) {
      console.log('Error: ', error);
    }
  };

  return (
    <View style={styles.mainContainer}>
      <Text style={styles.title}>Registration Form</Text>
      <View style={styles.line} />
      <SafeAreaView style={styles.sectionContainer}>
        <Text>Email</Text>
        <TextInput
          style={styles.input}
          onChangeText={setEmail}
          placeholder="stanley@email.com"
          inputMode="email"
          value={email}
        />
      </SafeAreaView>
      <SafeAreaView style={styles.sectionContainer}>
        <Text>Ticket</Text>
        <RadioGroup
          radioButtons={tickets}
          onPress={updateSelectedTicket}
          selectedId={selectedTicket}
          layout="row"
        />
      </SafeAreaView>
      <SafeAreaView style={styles.sectionContainer}>
        <Text>Quantity</Text>
        <TextInput
          style={styles.input}
          onChangeText={updateTotal}
          placeholder="2"
          inputMode="numeric"
          value={quantity}
        />
      </SafeAreaView>
      <SafeAreaView style={styles.sectionContainer}>
        <Button
          title={`Pay NGN ${new Intl.NumberFormat().format(total)}`}
          color={'#000'}
          onPress={submitForm}
        />
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  mainContainer: {
    marginVertical: 32,
    paddingHorizontal: 32,
  },
  input: {
    height: 40,
    borderWidth: 1,
    borderRadius: 4,
    borderColor: '#3d3d3d',
    padding: 10,
    marginTop: 4,
  },
  sectionContainer: {
    marginTop: 32,
  },
  title: {
    fontSize: 24,
    fontWeight: '600',
    marginTop: 32,
    marginBottom: 12,
  },
  button: {
    backgroundColor: '#000',
  },
  sectionDescription: {
    marginTop: 8,
    fontSize: 18,
    fontWeight: '400',
  },
  highlight: {
    fontWeight: '700',
  },
  line: {
    borderBottomColor: '#bababa',
    borderBottomWidth: StyleSheet.hairlineWidth,
  },
});

export default App;
