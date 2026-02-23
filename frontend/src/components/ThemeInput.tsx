import { useState } from "react";

type ThemeInputProps = {
  onSubmit: (theme: string) => void
}
function ThemeInput({onSubmit}: ThemeInputProps){
    const [theme,setTheme]=useState<string>("")
    const [error,setError]=useState<string>("")
    const handleSubmit=(e:React.FormEvent)=>{
        e.preventDefault()
        if (!theme.trim()){
            setError("Please enter a theme name")
            return
        }
        onSubmit(theme);

    }
    return <div className="theme-input-container">
        <h2>Generate your adventure</h2>
         <p>Enter a theme for you interactive story</p>
         <form onSubmit={handleSubmit}>
            <div className="input-group">
                <input type="text" value={theme} onChange={e=>setTheme(e.target.value)} placeholder="enter a theme" className={error?'error':''}/>
                {error &&<p className="error-text">{error}</p>}
                <button type="submit" className="generate-btn">
                    generate story
                </button>
            </div>
         </form>
    </div>
}
export default ThemeInput