const express = require("express");
const { log } = require("node:console");
const app = express();

app.get("/", (req, res) => {
  console.log("Hihi");
    res.json({
        status: "online"
    });
});

app.listen(process.env.PORT || 3000, "0.0.0.0");