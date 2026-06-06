const express = require("express");
const multer = require("multer");
const cors = require("cors");

const app = express();

app.use(cors());

const upload = multer({
    storage: multer.memoryStorage()
});

app.post("/upload", upload.single("image"), async (req, res) => {
    try {
        const image = req.file;
        const timestamp = req.body.timestamp;

        if (!image) {
            return res.status(400).json({
                status: "error",
                message: "No image uploaded",
                id: null
            });
        }

        console.log("Image:", image.originalname);
        console.log("Timestamp:", timestamp);

        // TODO:
        // Send image.buffer to AI model

        res.json({
            status: "success",
            message: "Image received",
            id: Date.now().toString()
        });

    } catch (err) {
        console.error(err);

        res.status(500).json({
            status: "error",
            message: err.message,
            id: null
        });
    }
});

app.listen(3000, () => {
    console.log("Server running on port 3000");
});