const express = require("express");
const multer = require("multer");

const app = express();
const PORT = process.env.PORT || 3000;

const upload = multer({
    storage: multer.memoryStorage()
});

app.post("/analyze", upload.single("image"), async (req, res) => {
    try {
        const image = req.file;
        const timestamp = req.body.timestamp;

        if (!image) {
            return res.status(400).json({
                success: false,
                message: "Image missing"
            });
        }

        console.log("Timestamp:", timestamp);
        console.log("Image Name:", image.originalname);
        console.log("Image Size:", image.size);

        // Process image here
        // Call Gemini/OpenAI/YOLO/etc

        const result = {
            detected_objects: ["person", "phone"],
            description: "Person holding a phone",
            timestamp: timestamp
        };

        res.json({
            success: true,
            result
        });

    } catch (error) {
        console.error(error);

        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on port ${PORT}`);
});