import { useState } from 'react'

// A short quiz shown once, before the main app, to gauge how spice-
// tolerant someone is. Each question's answer is worth 1-5 points;
// we average them into a single 1-5 "tolerance" score and hand that
// back to App via onComplete, which stores it and moves on.
const QUESTIONS = [
  {
    text: 'A dish is labeled "mild" on the menu. What do you expect?',
    options: [
      { label: 'Basically no heat at all', points: 1 },
      { label: 'A gentle warmth', points: 2 },
      { label: "Enough that I'll notice it", points: 3 },
      { label: "I'll add my own chili anyway", points: 4 },
      { label: '"Mild" means nothing to me', points: 5 },
    ],
  },
  {
    text: "How do you feel about ghost pepper or Carolina Reaper anything?",
    options: [
      { label: 'Absolutely not', points: 1 },
      { label: "I'd try a tiny bit, nervously", points: 2 },
      { label: "I'm curious but cautious", points: 3 },
      { label: "Sign me up", points: 4 },
      { label: "I've done it for fun before", points: 5 },
    ],
  },
  {
    text: 'Your go-to order at a Thai restaurant?',
    options: [
      { label: 'Something not spicy at all', points: 1 },
      { label: 'Mild, maybe 1 star', points: 2 },
      { label: 'Medium, 2-3 stars', points: 3 },
      { label: 'Thai spicy, 4+ stars', points: 4 },
      { label: '"As spicy as you can make it"', points: 5 },
    ],
  },
]

function OnboardingQuiz({ onComplete }) {
  // One answer slot per question, all starting unanswered (null).
  const [answers, setAnswers] = useState(QUESTIONS.map(() => null))

  function selectAnswer(questionIndex, points) {
    const updated = [...answers]
    updated[questionIndex] = points
    setAnswers(updated)
  }

  const allAnswered = answers.every((a) => a !== null)

  function handleSubmit() {
    const total = answers.reduce((sum, points) => sum + points, 0)
    const tolerance = Math.round(total / QUESTIONS.length)
    onComplete(tolerance)
  }

  return (
    <div className="quiz">
      <h2>How spicy do you like it?</h2>
      <p>Quick 3-question quiz so we know your spice tolerance.</p>

      {QUESTIONS.map((question, questionIndex) => (
        <div className="quiz-question" key={question.text}>
          <p>{question.text}</p>
          {question.options.map((option) => (
            <label key={option.label} className="quiz-option">
              <input
                type="radio"
                name={`question-${questionIndex}`}
                checked={answers[questionIndex] === option.points}
                onChange={() => selectAnswer(questionIndex, option.points)}
              />
              {option.label}
            </label>
          ))}
        </div>
      ))}

      <button onClick={handleSubmit} disabled={!allAnswered}>
        See my results
      </button>
    </div>
  )
}

export default OnboardingQuiz
