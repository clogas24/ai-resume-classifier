document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/profile_jobs')
      .then(response => response.json())
      .then(data => {
        console.log("Profile jobs:", data);
  
        const likedContainer = document.getElementById('liked-jobs');
        const savedContainer = document.getElementById('saved-jobs');
        const dislikedContainer = document.getElementById('disliked-jobs');
  
        likedContainer.innerHTML = '';
        savedContainer.innerHTML = '';
        dislikedContainer.innerHTML = '';
  
        function createJobCard(job, container) {
          const div = document.createElement('div');
          div.classList.add('job-posting');
          div.innerHTML = `
            <h4><a href="${job.url}" target="_blank">${job.title}</a></h4>
            <p><strong>${job.company}</strong> - ${job.location}</p>
            <button onclick="removeJob(${job.job_id}, this)">🗑️ Remove</button>
            <hr>
          `;
          container.appendChild(div);
        }
  
        if (data.liked.length === 0) {
          likedContainer.innerHTML = '<p>No liked jobs yet.</p>';
        } else {
          data.liked.forEach(job => createJobCard(job, likedContainer));
        }
  
        if (data.saved.length === 0) {
          savedContainer.innerHTML = '<p>No saved jobs yet.</p>';
        } else {
          data.saved.forEach(job => createJobCard(job, savedContainer));
        }
  
        if (data.disliked.length === 0) {
          dislikedContainer.innerHTML = '<p>No disliked jobs yet.</p>';
        } else {
          data.disliked.forEach(job => createJobCard(job, dislikedContainer));
        }
      })
      .catch(error => {
        console.error("Profile jobs fetch error:", error);
        document.getElementById('liked-jobs').innerHTML = '<p>Error loading liked jobs.</p>';
        document.getElementById('saved-jobs').innerHTML = '<p>Error loading saved jobs.</p>';
        document.getElementById('disliked-jobs').innerHTML = '<p>Error loading disliked jobs.</p>';
      });
  });
  
  function removeJob(jobId, button) {
    fetch('/api/remove_job', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ job_id: jobId })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        const jobCard = button.closest('.job-posting');
        if (jobCard) {
          jobCard.remove();
        }
      }
    })
    .catch(error => {
      console.error("Remove job error:", error);
    });
  }  