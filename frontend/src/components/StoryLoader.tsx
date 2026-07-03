import { useEffect, useState } from "react"
import { useParams, useNavigate } from "react-router-dom"
import axios, { AxiosError } from "axios"
import LoadingStatus from "./LoadingStatus"
import StoryGame from "./StoryGame"

// 根据环境判断：本地用 /api (Vite 代理)，生产用完整 URL
const API_BASE_URL = 
  typeof window !== 'undefined' && window.location.hostname === 'localhost'
    ? '/api'
    : 'https://myadventure.onrender.com/api'

type Story = any 

export default function StoryLoader() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [story, setStory] = useState<Story | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return

    const loadStory = async () => {
      setLoading(true)
      setError(null)

      try {
        const response = await axios.get(
          `${API_BASE_URL}/stories/${id}/complete`
        )
        setStory(response.data)
      } catch (err) {
        const axiosError = err as AxiosError

        if (axiosError.response?.status === 404) {
          setError("Story not found")
        } else {
          setError("Failed to load story")
        }
      } finally {
        setLoading(false)
      }
    }

    loadStory()
  }, [id])

  const createNewStory = () => {
    navigate("/")
  }

  if (loading) {
    return <LoadingStatus theme="story" />
  }

  if (error) {
    return (
      <div className="story-loader">
        <div className="error-message">
          <h2>Story not found</h2>
          <p>{error}</p>
          <button onClick={createNewStory}>
            Go to story generator
          </button>
        </div>
      </div>
    )
  }

  if (story) {
    return (
      <div className="story-loader">
        <StoryGame story={story} onNewStory={createNewStory} />
      </div>
    )
  }

  return null
}
