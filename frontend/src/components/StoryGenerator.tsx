import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import axios from "axios"
import ThemeInput from "./ThemeInput"
import LoadingStatus from "./LoadingStatus"

const API_BASE_URL = "/api"

type JobStatus = "pending" | "processing" | "completed" | "failed"

export default function StoryGenerator() {
  const navigate = useNavigate()
  const [theme, setTheme] = useState<string>("")
  const [jobId, setJobId] = useState<string | null>(null)
  const [jobStatus, setJobStatus] = useState<JobStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(false)

  useEffect(() => {
    let pollInterval: number | undefined
    if (jobId && jobStatus === "processing") {
      pollInterval = window.setInterval(() => {
        pollJobStatus(jobId)
      }, 5000)
    }
    return () => {
      if (pollInterval) {
        clearInterval(pollInterval)
      }
    }
  }, [jobId, jobStatus])

  const generateStory = async (theme: string) => {
    setLoading(true)
    setError(null)
    setTheme(theme)
    try {
      const response = await axios.post(`${API_BASE_URL}/stories/create`, { theme })
      const { job_id, status } = response.data
      setJobId(job_id)
      setJobStatus(status)
      pollJobStatus(job_id)
    } catch (e: any) {
      setLoading(false)
      setError(`Failed to check story status: ${e.message}`)
    }
  }

  const pollJobStatus = async (id: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/jobs/${id}`)
      const { status, story_id, error: jobError } = response.data
      setJobStatus(status)
      if (status === "completed" && story_id) {
        fetchStory(story_id)
      } else if (status === "failed" || jobError) {
        setError(jobError || "Failed to generate story")
        setLoading(false)
      }
    } catch (e: any) {
      if (e.response?.status !== 404) {
        setError(`Failed to check story status: ${e.message}`)
        setLoading(false)
      }
    }
  }

  const fetchStory = async (id: string) => {
    try {
      setLoading(false)
      setJobStatus("completed")
      navigate(`/story/${id}`)
    } catch (e: any) {
      setError(`Failed to load story: ${e.message}`)
      setLoading(false)
    }
  }

  const reset = () => {
    setJobId(null)
    setJobStatus(null)
    setError(null)
    setTheme("")
    setLoading(false)
  }

  return (
    <div className="story-generator">
      {error && (
        <div className="error-message">
          <p>{error}</p>
          <button onClick={reset}>Try Again</button>
        </div>
      )}

      {!jobId && !error && !loading && <ThemeInput onSubmit={generateStory} />}
      {loading && <LoadingStatus theme={theme} />}
    </div>
  )
}
