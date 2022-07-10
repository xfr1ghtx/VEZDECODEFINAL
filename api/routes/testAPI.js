var express = require("express");
var router = express.Router();
var messages = []

const fs = require('fs')

fs.readFile("./routes/small.json", (err, data) => {
    if (err) {
        console.error(err)
        return
    }
    messages = JSON.parse(data)
})


router.get("/", function (req, res, next) {
    let ans = JSON.stringify(messages)
    res.send(ans);
});


router.post("/read", function (req, res, next) {
    let emails = req.body.emails
    messages.forEach(m => {
        if (emails.findIndex((element, index, array) => m.author.email == element)!=-1) {
            m.read = true
        }
    });
    res.send(JSON.stringify(messages))
});


router.post("/unread", function (req, res, next) {
    let emails = req.body.emails
    messages.forEach(m => {
        if (emails.findIndex((element, index, array) => m.author.email == element)!=-1) {
            m.read = false
        }
    });
    res.send(JSON.stringify(messages))
});




module.exports = router;
