import { useState, useEffect } from "react"

type StoryOption = {
  node_id: string
  text: string
}

type StoryNode = {
  id: string
  content: string
  is_ending: boolean
  is_winning_ending: boolean
  options?: StoryOption[]
}

type Story = {
  title: string
  root_node: { id: string }
  all_nodes: Record<string, StoryNode>
}

type StoryGameProps = {
  story: Story | null
  onNewStory?: () => void
}

export default function StoryGame({ story, onNewStory }: StoryGameProps) {
  const [currentNodeId, setCurrentNodeId] = useState<string | null>(null)
  const [currentNode, setCurrentNode] = useState<StoryNode | null>(null)
  const [options, setOptions] = useState<StoryOption[]>([])
  const [isEnding, setIsEnding] = useState(false)
  const [isWinningEnding, setIsWinningEnding] = useState(false)

  useEffect(() => {
    if (story?.root_node) {
      setCurrentNodeId(story.root_node.id)
    }
  }, [story])

  useEffect(() => {
    if (currentNodeId && story?.all_nodes) {
      const node = story.all_nodes[currentNodeId]
      if (!node) return

      setCurrentNode(node)
      setIsEnding(node.is_ending)
      setIsWinningEnding(node.is_winning_ending)

      if (!node.is_ending && node.options && node.options.length > 0) {
        setOptions(node.options)
      } else {
        setOptions([])
      }
    }
  }, [currentNodeId, story])

  const chooseOption = (optionId: string) => {
    setCurrentNodeId(optionId)
  }

  const restartStory = () => {
    if (story?.root_node) {
      setCurrentNodeId(story.root_node.id)
    }
  }

  if (!story) return null

  return (
    <div className="story-game">
      <header className="story-header">
        <h2>{story.title}</h2>
      </header>

      <div className="story-content">
        {currentNode && (
          <div className="story-node">
            <p>{currentNode.content}</p>

            {isEnding ? (
              <div className="story-ending">
                <h3>{isWinningEnding ? "Congratulations" : "The End"}</h3>
                <p>
                  {isWinningEnding
                    ? "You reached a winning ending"
                    : "Your adventure has ended."}
                </p>
              </div>
            ) : (
              <div className="story-options">
                <h3>What will you do?</h3>
                <div className="options-list">
                  {options.map((option) => (
                    <button
                      key={option.node_id}
                      onClick={() => chooseOption(option.node_id)}
                      className="option-btn"
                    >
                      {option.text}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        <div className="story-controls">
          <button onClick={restartStory} className="reset-btn">
            Restart Story
          </button>
        </div>

        {onNewStory && (
          <button onClick={onNewStory} className="new-story-btn">
            New Story
          </button>
        )}
      </div>
    </div>
  )
}
