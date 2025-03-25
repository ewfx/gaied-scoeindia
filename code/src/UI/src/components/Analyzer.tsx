import React, { useState } from "react";
import "../components/assets/styles.css";

const Analyzer = () => {
    const [sender, setSender] = useState("");
    const [subject, setSubject] = useState("Test email");
    const [userDisputesDuplicate, setUserDisputesDuplicate] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [result, setResult] = useState<any>(null);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files.length > 0) {
            setFile(e.target.files[0]);
        }
    };

    const handleAnalyze = async () => {
        if (!file) {
            alert("Please upload a file.");
            return;
        }

        const formData = new FormData();
        const requestPayload = {
            file_path: file.name, // Dynamically setting file path
            sender,
            subject,
            user_disputes_duplicate: !userDisputesDuplicate,
        };

        formData.append("request_data", JSON.stringify(requestPayload));
        formData.append("file", file);

        try {
            const response = await fetch("http://127.0.0.1:8000/classify_email", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (data.error) {
                alert(`Error: ${data.error}`);
            } else {
                setResult(data);
            }
        } catch (error) {
            console.error("Error calling API:", error);
            alert("Failed to connect to backend API.");
        }
    };

    return (
        <div className='container'>
            <header className='header'>AI-Powered Email Classification</header>

            <main className='content'>
                <h1>Email Classification</h1>

                <div className='form-container'>
                    {/* Sender Input */}
                    <div className='input-group'>
                        <label className='input-label' htmlFor='sender'>
                            Sender:
                        </label>
                        <input
                            id='sender'
                            type='text'
                            className='input-field'
                            placeholder='Enter sender name...'
                            value={sender}
                            onChange={(e) => setSender(e.target.value)}
                        />
                    </div>

                    {/* Subject Input */}
                    <div className='input-group'>
                        <label className='input-label' htmlFor='subject'>
                            Subject:
                        </label>
                        <input id='subject' type='text' className='input-field' value={subject} onChange={(e) => setSubject(e.target.value)} />
                    </div>

                    {/* Check Duplicate Checkbox */}
                    <div className='checkbox-group'>
                        <input
                            type='checkbox'
                            id='duplicate-check'
                            checked={userDisputesDuplicate}
                            onChange={(e) => setUserDisputesDuplicate(e.target.checked)}
                        />
                        <label htmlFor='duplicate-check'>Check Duplicate</label>
                    </div>

                    {/* File Upload */}
                    <div className='upload-box'>
                        <input type='file' onChange={handleFileChange} />
                        {file && <p>Selected file: {file.name}</p>}
                    </div>

                    {/* Analyze Button */}
                    <button className='analyze-btn' onClick={handleAnalyze}>
                        Analyze Now
                    </button>

                    {/* ✅ Result section */}
                    {result && (
                        <div className='result-box'>
                            <div>
                                <h3>
                                    <span role='img' aria-label='document'>
                                        📝
                                    </span>{" "}
                                    Classification:
                                </h3>
                                <ul>
                                    {result.classification.map((item: any, index: number) => (
                                        <li key={index}>
                                            <strong>Request Type:</strong> {item.request_type} <br />
                                            <strong>Sub-Request:</strong> {item.sub_request_type} <br />
                                            <strong>Confidence:</strong> {item.confidence_score}
                                        </li>
                                    ))}
                                </ul>

                                {/* Duplicate Email Warning */}
                                {result.is_duplicate && (
                                    <div className='duplicate-warning'>
                                        <span role='img' aria-label='warning'>
                                            🚨
                                        </span>{" "}
                                        <strong>Duplicate Email Detected!</strong>
                                        <p>Reason: {result.reason}</p>
                                        <p>Score: {result.score}</p>
                                        <p>Duplicate ID: {result.duplicate_email_id}</p>
                                    </div>
                                )}

                                {/* Extracted Context */}
                                <h3>
                                    <span role='img' aria-label='pin'>
                                        📌
                                    </span>{" "}
                                    Extracted Context:
                                </h3>
                                <pre>{JSON.stringify(result.extracted_context, null, 2)}</pre>
                            </div>
                        </div>
                    )}
                </div>
            </main>

            <footer className='footer'>© 2025 . All rights reserved. AI-Powered Email Classification</footer>
        </div>
    );
};

export default Analyzer;
