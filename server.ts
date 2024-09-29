// server.ts

import express, { Request, Response } from "express";
import axios from "axios";
import fs from "fs";
import path from "path";
import { analyzeReviews } from "./utils/ai.util"; // Adjust the path as necessary
import cors from "cors";

const app = express();

app.use(express.json());
app.use(cors());
const port = process.env.PORT || 3001;

// Interface for the expected structure of the reviews JSON file
interface Review {
  reviewId: string;
  userName: string;
  content: string;
  score: number;
  thumbsUpCount: number;
  reviewCreatedVersion: string | null;
}

interface AppDetails {
  // Define properties as needed or use any if the structure is unknown
  [key: string]: any;
}

interface ReviewsData {
  app: AppDetails;
  reviews: Review[];
}

// Function to wait for a file to be created
function waitForFile(
  filePath: string,
  timeout = 10000,
  interval = 500
): Promise<void> {
  return new Promise<void>((resolve, reject) => {
    const startTime = Date.now();

    const checkExistence = () => {
      fs.access(filePath, fs.constants.F_OK, (err) => {
        if (!err) {
          resolve();
        } else if (Date.now() - startTime > timeout) {
          reject(
            new Error("Timeout waiting for file to be created : " + filePath)
          );
        } else {
          setTimeout(checkExistence, interval);
        }
      });
    };

    checkExistence();
  });
}

app.post("/analyze-reviews", async (req, res) => {
  console.log("Received request:", req.body);
  const appId = req.body.appId as string;

  if (!appId) {
    res.status(400).json({ error: "Missing appId parameter" });
    return;
  }

  try {
    // Call the Python API to fetch reviews
    const pythonApiUrl = `http://localhost:3002/fetch-reviews?appId=${encodeURIComponent(
      appId
    )}`;
    const response = await axios.get(pythonApiUrl);

    console.log("Response from Python API:", response.data);

    // Wait for the reviews file to be saved
    const filePath = path.join(__dirname, `../${appId}_reviews.json`);
    await waitForFile(filePath);

    // Read and parse the reviews file
    const fileData = fs.readFileSync(filePath, "utf-8");
    const jsonData: ReviewsData = JSON.parse(fileData);

    // Extract the review contents
    const reviews = jsonData.reviews.map((review: Review) => review.content);

    // Analyze the reviews using the LLM
    const analysisResult = await analyzeReviews(reviews);

    // Return the analysis result as JSON
    res.json(JSON.parse(analysisResult));
  } catch (error) {
    console.error("Error processing request:", error);
    res.status(500).json({ error: "Failed to process the request" });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
