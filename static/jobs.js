document.addEventListener('DOMContentLoaded', () => {
  const jobCategory = localStorage.getItem('predictedCategory');

  if (!jobCategory) {
    document.getElementById('jobsContainer').innerHTML = "<p>No job category found. Please upload your resume first.</p>";
    return;
  }

  const query = encodeURIComponent(jobCategory);
  const url = `/api/jobs?category=${query}`;

  // Show what category is being searched
  document.getElementById('jobsContainer').insertAdjacentHTML(
    'beforebegin',
    `<p><strong>Searching for jobs in:</strong> ${jobCategory}</p>`
  );

  fetch(url)
    .then(response => response.json())
    .then(data => {
      console.log("JSearch data:", data);  // Debug log
      const container = document.getElementById('jobsContainer');
      container.innerHTML = "";

      const jobs = data.data;
      if (!jobs || jobs.length === 0) {
        container.innerHTML = `
          <p>No jobs found for this category.</p>
          <p>Try uploading a resume with more specific job skills or experience.</p>
        `;
        return;
      }

      jobs.forEach(job => {
        const div = document.createElement('div');
        div.className = "job-posting";

        // Use job.job_id if available; otherwise fallback to random ID (for safety)
        const jobId = job.job_id || Math.floor(Math.random() * 1000000);

        div.innerHTML = `
          <h3><a href="${job.job_apply_link}" target="_blank">${job.job_title}</a></h3>
          <p><strong>${job.employer_name}</strong></p>
          <p>Location: ${job.job_city || job.job_country || "Remote"}</p>
          <div class="job-posting-buttons">
            <button onclick="saveJob('${jobId}', 'liked', this)">👍 Like</button>
            <button onclick="saveJob('${jobId}', 'saved', this)">📌 Save</button>
            <button onclick="saveJob('${jobId}', 'disliked', this)">👎 Dislike</button>
          </div>
          <hr>
        `;
        container.appendChild(div);
      });
    })
    .catch(error => {
      document.getElementById('jobsContainer').innerHTML = `<p>Error loading jobs: ${error.message}</p>`;
      console.error("Job fetch error:", error);
    });
});

// Save the job based on user interaction
function saveJob(jobId, status, button) {
  fetch('/api/save_job', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      job_id: jobId,
      status: status
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      console.log(`Job ${jobId} marked as ${status}`);
      // Remove the job card from the page
      const jobPosting = button.closest('.job-posting');
      if (jobPosting) {
        jobPosting.remove();
      }
    } else {
      console.error('Error saving job');
    }
  })
  .catch(err => console.error('Fetch error:', err));
}