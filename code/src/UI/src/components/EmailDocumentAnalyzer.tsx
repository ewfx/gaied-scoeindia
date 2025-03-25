import React, { useState } from "react";
import axios from "axios";
import "../App.css"; // Make sure to import the CSS file
//import "../../App.css";

const EmailDocumentAnalyzer: React.FC = () => {
    const [activeTab, setActiveTab] = useState("email");
    const [emailText, setEmailText] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [analysisResult, setAnalysisResult] = useState("");

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setFile(event.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        const formData = new FormData();
        if (activeTab === "email") {
            formData.append("email_text", emailText);
        } else if (file) {
            formData.append("file", file);
        }

        try {
            const response = await axios.post("http://127.0.0.1:8000/analyze", formData, {
                headers: { "Content-Type": "multipart/form-data" },
            });
            setAnalysisResult(response.data.result);
        } catch (error) {
            console.error("Error analyzing:", error);
        }
    };

    return (
        <div className='container'>
            {/* Header */}
            <header className='header'>Email & Document Analyzer</header>

            {/* Main Content */}
            <div className='card'>
                <h2>Analyze Emails & Documents</h2>

                {/* Tabs */}
                <div className='tabs'>
                    <button className={activeTab === "email" ? "active" : ""} onClick={() => setActiveTab("email")}>
                        Email
                    </button>
                    <button className={activeTab === "document" ? "active" : ""} onClick={() => setActiveTab("document")}>
                        Document
                    </button>
                </div>

                {/* Email Input */}
                {activeTab === "email" && (
                    <textarea
                        className='textarea'
                        rows={6}
                        placeholder='Paste your email here...'
                        value={emailText}
                        onChange={(e) => setEmailText(e.target.value)}
                    />
                )}

                {/* Document Upload */}
                {activeTab === "document" && (
                    <div className='upload-box'>
                        <input type='file' id='fileUpload' onChange={handleFileChange} />
                        {file && <p>Selected: {file.name}</p>}
                    </div>
                )}

                {/* Analyze Button */}
                <button className='analyze-button' onClick={handleAnalyze}>
                    Analyze Now
                </button>

                {/* Results */}
                {analysisResult && (
                    <div className='result-box'>
                        <strong>Result:</strong> {analysisResult}
                    </div>
                )}
            </div>

            {/* Footer */}
            <footer className='footer'>© 2025 Email & Document Analyzer. All rights reserved.</footer>
        </div>
    );
};

export default EmailDocumentAnalyzer;
