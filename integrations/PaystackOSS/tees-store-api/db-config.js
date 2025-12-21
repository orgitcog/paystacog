require('dotenv').config()
var mysql = require('mysql');

// Create mysql connection using env variables.
var connection = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASS,
    database: process.env.DATABASE
});

connection.connect(function (err) {
    if (err) throw err;
    console.log("DB Connected!")
})

module.exports = connection