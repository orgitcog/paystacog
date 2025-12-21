const { result, each } = require('lodash');

require('dotenv').config()
const express = require('express'),
    cors = require('cors'),
    axios = require('axios'),
    crypto = require('crypto'),
    db = require('./db-config.js'),
    port = process.env.PORT || 3000;


const app = express();
app.use(cors());
app.use(express.urlencoded({
    extended: true
}))
app.use(express.json())
app.use(require('sanitize').middleware);


// Setting up Paystack configurations.
const pstk_secret = process.env.PSTK_SECRET_KEY // Never commit secret keys to the repo.
const paystack_api = 'https://api.paystack.co/'
const paystack_headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${pstk_secret}`
}

axios.create({ paystack_api, responseType: 'json' })

app.get('/', (req, res) => {
    console.log(req)
    res.send('Hello World!')
});

//Make payment
app.post('/payment', (req, res) => {
    const params = {
        'email': req.body.email,
        'amount': req.body.amount
    }
    // Create transaction on Paystack.
    axios.post(`${paystack_api}transaction/initialize`, params, { headers: paystack_headers }).then((result) => {
        console.log(result.data);

        // Store order in the db...
        createOrder(result.data.data.reference)
        return res.send({
            "checkout_url": result.data.data.authorization_url,
            "access_code": result.data.data.access_code
        })
    }, (error) => {
        console.log(error);
        res.send({
            'status': false,
            'message': "something went wrong"
        })
    })
})

// Make payment using an existing card.
app.post('/charge', (req, res) => {
    const params = {
        'email': req.body.email,
        'amount': req.body.amount,
        'authorization_code': req.body.auth_code
    }
    axios.post(`${paystack_api}charge`, params, { headers: paystack_headers }).then((result) => {
        console.log(result);
        // create order in database.
        createOrder(result.data.data.reference)
        res.send({
            "status": result.data.status,
            "message": result.data.message
        })
    }, (error) => {
        console.log(error);
        res.send({
            'status': false,
            'message': "something went wrong"
        })
    })

})
// Fetch an authorization
app.get('/authorizations', (req, res) => {
    var auth_code = req.query.email
    fetchAuthorizations(auth_code).then((result) => {
        res.send({
            'status': true,
            'tokens': result
        })
    })
})

// Webhook url listener. Save the authorization and marks the order as successfully paid.
app.post('/paystack-webhook', (req, res) => {

    // Validate the event is from Paystack
    var hash = crypto.createHmac('sha512', pstk_secret).update(JSON.stringify(req.body)).digest('hex');

    if (hash == req.headers['x-paystack-signature']) {
        //respond with 200 OK first
        res.sendStatus(200)

        //store the customer's email and auth_code for future charges.
        storeAuthorization(req.body.data)
        // update the the order status to success
        updateOrder(req.body.data.reference)
    }
})

// Create the order after successful transaction initialization
function createOrder(order_ref) {
    let sql_create = `INSERT into Orders (order_ref, status) VALUES ('${order_ref}', 'pending')`;

    db.query(sql_create, function (err, result) {
        if (err) throw err;
        console.log(result);
    })
}

// Update an order to success when webhook is fired.
function updateOrder(order_ref) {
    const sql_update = `UPDATE Orders SET status = 'success' WHERE order_ref = '${order_ref}'`;

    db.query(sql_update, function (err, result) {
        if (err) throw err;
        console.log(result);
    })
}
// Save the customer's card token for a return transaction...
function storeAuthorization(data) {
    let email = data.customer.email
    let auth_code = data.authorization.authorization_code
    let brand = data.authorization.card_type
    let last_four = data.authorization.last4

    const sql_createAuth = `INSERT into Tokens (email, auth_code, brand, last_four) 
                        VALUES ('${email}', '${auth_code}', '${brand}', '${last_four}')`

    db.query(sql_createAuth, function (err, result) {
        if (err) throw err;
        console.log(result);
    })
}

// Get all authorizations tied to an email
function fetchAuthorizations(email) {
    const sql_fetch = `SELECT * from Tokens where email = ?`;

    return new Promise((resolve, reject) => {
        db.query(sql_fetch, [email], function (err, result) {
            if (err) {
                throw err;
            }
            
            resolve(result)
        })
    })

}

app.listen(port, () => {
    console.log(`Server listening on port ${port}!`)
});