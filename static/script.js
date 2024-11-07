async function castVote(candidate) {
  const response = await fetch("/vote", {
      method: "POST",
      headers: {
          "Content-Type": "application/json"
      },
      body: JSON.stringify({ candidate: candidate })
  });
  const data = await response.json();
  document.getElementById("vote-message").textContent = data.message;
}

function showResults() {
  // You can replace the content dynamically here
  fetch('/results')
      .then(response => response.json())
      .then(data => {
          const resultsList = document.getElementById('results-list');
          const resultsDisplay = document.getElementById('results-display');
          
          resultsList.innerHTML = ''; // Clear previous results

          // Loop through and display the results
          for (const [candidate, votes] of Object.entries(data.votes)) {
              const li = document.createElement('li');
              li.textContent = `${candidate}: ${votes} votes`;
              if (candidate === data.winner) {
                  li.classList.add('winner'); // Highlight the winner
              }
              resultsList.appendChild(li);
          }

          // Show the results section
          resultsDisplay.style.display = 'block';
      })
      .catch(error => console.error('Error fetching results:', error));
}

