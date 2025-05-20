// txt
async function classifyResume() {
  const resume = document.getElementById("resumeInput").value;
  const resultDiv = document.getElementById("result");

  if (!resume.trim()) {
    resultDiv.textContent = "Please paste a resume first.";
    return;
  }

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume: resume }),
    });

    const data = await response.json();

    if (data.predicted_job_category) {
      localStorage.setItem("predictedCategory", data.predicted_job_category); // store for jobs page
      resultDiv.textContent = "Predicted Job Category: " + data.predicted_job_category;
    } else {
      resultDiv.textContent = "Error: " + (data.error || "Unknown issue");
    }
  } catch (err) {
    resultDiv.textContent = "Error: " + err.message;
  }
}

// pdf
async function uploadPDF() {
  const fileInput = document.getElementById("resumeFile");
  const resultDiv = document.getElementById("result");

  if (!fileInput.files.length) {
    resultDiv.textContent = "Please select a PDF file first.";
    return;
  }

  const formData = new FormData();
  formData.append("resume", fileInput.files[0]);

  try {
    const response = await fetch("/upload", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (data.predicted_job_category) {
      localStorage.setItem("predictedCategory", data.predicted_job_category); // store for jobs page
      resultDiv.textContent = "Predicted Job Category: " + data.predicted_job_category;
    } else {
      resultDiv.textContent = "Error: " + (data.error || "Unknown issue");
    }
  } catch (err) {
    resultDiv.textContent = "Error: " + err.message;
  }
}