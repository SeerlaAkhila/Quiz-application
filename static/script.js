document.addEventListener('DOMContentLoaded', () => {

    // --- Element Selections ---
    const quizForm = document.getElementById('quiz-form');
    const timerElement = document.getElementById('timer');
    const resultModal = document.getElementById('result-modal');
    const resultText = document.getElementById('result-text');
    const nameInput = document.getElementById('name');
    const modalContent = resultModal.querySelector('div');

    // --- Timer Logic ---
    let timeLeft = 600; // 10 minutes in seconds
    let timerInterval;

    function updateTimer() {
        const minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        // Pad seconds with a leading zero if less than 10
        seconds = seconds < 10 ? '0' + seconds : seconds;
        timerElement.textContent = `${minutes}:${seconds}`;

        // Change timer color to red in the last minute
        if (timeLeft <= 60) {
            timerElement.classList.remove('bg-indigo-500');
            timerElement.classList.add('bg-red-500');
        }

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timerElement.textContent = "Time's Up!";
            submitQuiz(); // Auto-submit when time is up
        } else {
            timeLeft--;
        }
    }

    // Start the timer as soon as the page loads
    timerInterval = setInterval(updateTimer, 1000);

    // --- Quiz Submission Logic ---
    quizForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission
        clearInterval(timerInterval); // Stop the timer on manual submission
        submitQuiz();
    });

    async function submitQuiz() {
        // Collect the answers from the form
        const formData = new FormData(quizForm);
        const answers = {};
        for (let [key, value] of formData.entries()) {
            // The key is like 'question_1', we extract the '1'
            const questionId = key.split('_')[1];
            answers[questionId] = value;
        }

        const name = nameInput.value.trim() || 'Anonymous';

        // --- API Call to Backend ---
        try {
            const response = await fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: name,
                    answers: answers
                }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            displayResult(result);

        } catch (error) {
            console.error("Error submitting quiz:", error);
            resultText.textContent = "Failed to submit quiz. Please try again.";
            showModal();
        }
    }

    // --- Display Result ---
    function displayResult(result) {
        resultText.textContent = `You scored ${result.score} out of ${result.total}.`;
        showModal();
    }

    // --- Modal Animation ---
    function showModal() {
        resultModal.classList.remove('hidden');
        // Use a short timeout to allow the display property to apply before starting the transition
        setTimeout(() => {
            modalContent.classList.remove('scale-95', 'opacity-0');
            modalContent.classList.add('scale-100', 'opacity-100');
        }, 10);
    }
});
