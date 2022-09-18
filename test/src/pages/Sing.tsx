import React, { useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import { Lrc, LrcLine, useRecoverAutoScrollImmediately } from 'react-lrc'
import { useHistory } from 'react-router'
import { serverUrl } from '../utils/constants'
import { DataContext } from '../utils/context'

interface LineProps {
  active: boolean
  content: string
}

const Line: React.FC<LineProps> = ({ active, content }) => {
  if (active) {
    return <div className='text-center text-sky-400 my-5'>{content}</div>
  }
  return <div className='text-center text-gray-200 my-5'>{content}</div>
}

export const Sing: React.FC = () => {
  const [play, setPlay] = useState(false)
  const [playBack, setPlayBack] = useState(false)
  const [hasVocal, setHasVocal] = useState(false)
  const [curTrack, setCurTrack] = useState<string>('')
  const [destination, setDestination] = useState<AudioDestinationNode>(null)
  const [mic, setMic] = useState<MediaStreamAudioSourceNode>(null)
  const [curKey, setKey] = useState(0)
  const [adjustKey, setAdjustKey] = useState(curKey)
  const [curTime, setCurTime] = useState(0)
  const data = useContext(DataContext)
  const [audioUrl, setAudioUrl] = useState(data.audioUrl)
  const [audioNvUrl, setAudioNvUrl] = useState(data.audioNvUrl)
  
  const audioRef = useRef<HTMLAudioElement>(null)
  const history = useHistory()

  const {
    signal,
  } = useRecoverAutoScrollImmediately()

  const lineRenderer = useCallback(
    ({ active, line: { content } }: { active: boolean; line: LrcLine }) => (
      <Line active={active} content={content}/>
    ),
    []
  )

  const keyShift = async () => {
    try {
      const res = await fetch(`${serverUrl}/get-shifted-audio`, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          shift_semitones: adjustKey,
          wav_path: data.audioUrl,
        }),
      })
      const body = await res.json()
      setAudioUrl(body.audioUrl)
      setAudioNvUrl(body.audioNvUrl)
    } catch (err) {
      console.error(err)
    }

    setKey(adjustKey)
  }

  useEffect(() => {
    if (hasVocal) {
      setCurTrack(audioUrl)
    } else {
      setCurTrack(audioNvUrl)
    }
  }, [audioUrl, audioNvUrl])

  const toggleVocal = async () => {
    setHasVocal(vocal => !vocal)
    setCurTrack(track => {
      if (hasVocal) {
        return audioNvUrl
      }
      return audioUrl
    })
    
  }

  useEffect(() => {
    if (!play) return
    (async () => {
      if (audioRef.current) {
        audioRef.current.currentTime = curTime
        await audioRef.current.play()
      }
    })()
  }, [curTrack])

  useEffect(() => {
    if (audioRef.current === null) return
    audioRef.current.addEventListener('play', () => setPlay(true))
    audioRef.current.addEventListener('pause', () => setPlay(false))
  }, [audioRef])

  useEffect(() => {
    if (audioRef.current === null) return
    audioRef.current.ontimeupdate = () => {
      setCurTime(audioRef.current.currentTime)
    }
  }, [audioRef])

  const togglePlayback = () => {
    setPlayBack((playback) => !playback)
  }

  const togglePlay = () => {
    setPlay((play) => {
      if (play) {
        audioRef.current.pause()
        return false
      }
      audioRef.current.play()
      return true
    })
  }

  const resetSettings = () => {
    setPlay(false)
    setPlayBack(false)
    setCurTime(0)
    setKey(0)
    setHasVocal(false)
    setAdjustKey(0)
  }

  useEffect(() => {
    initPlayback()
    if (data) {
      setAudioUrl(data.audioUrl)
      setAudioNvUrl(data.audioNvUrl)
      setCurTrack(data.audioNvUrl)
    }

    return resetSettings
  }, [data])

  useEffect(() => {
    if (destination === null || mic === null) return
    if (playBack) {
      mic.connect(destination)
    }
    else {
      mic.disconnect()
    }
  }, [destination, mic, playBack])

  const initPlayback = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: {
        echoCancellation: false,
        noiseSuppression: false,
        autoGainControl: false,
        latency: 0,
      }})
    const audioContext = new AudioContext({
      latencyHint: 'playback',
    })
    const mic = audioContext.createMediaStreamSource(stream)
    setDestination(audioContext.destination)
    setMic(mic)
  }

  const newSong = () => {
    history.push('/app')
  }

  return (
    <>
      <div className="bg-[url('/assets/sample.webp')] bg-no-repeat bg-cover hover:cursor-pointer z-0 absolute h-full w-full"/>
      <div className='bg-black absolute z-[5] h-full w-full opacity-60'/>
      <div className='text-3xl font-sans w-screen h-screen flex flex-row text-white z-10 relative'>
        <div className='flex-1 bg-gradient-to-b from-slate-800 to-cyan-800 flex flex-col text-base text-center px-2 py-4'>
          <div>Key change (semitones): {curKey > 0 ? `+${curKey}` : curKey} </div>
          <div>Modification: {adjustKey > 0 ? `+${adjustKey}` : adjustKey} </div>
          <div className='flex flex-row  align-middle my-1'>
            <button className='p-auto border flex-1 rounded-tl rounded-bl' onClick={() => setAdjustKey(key => key - 1)}>key -</button>
            <button className='p-auto border flex-1 rounded-tr rounded-br' onClick={() => setAdjustKey(key => key + 1)}>key +</button>
          </div>
          <button className='p-auto border rounded' onClick={keyShift}>Apply</button>
          <div className='mt-5'>Vocal: {hasVocal ? 'enabled' : 'disabled'}</div>
          <button onClick={toggleVocal} className='p-auto border my-1 rounded'>{hasVocal ? 'Disable vocal' : 'Enable vocal'}</button>
          <div className='mt-5'>Playback: {playBack ? 'enabled' : 'disabled'}</div>
          <button onClick={togglePlayback} className='p-auto border my-1 rounded'>{playBack ? 'Disable playback' : 'Enable playback'}</button>

          <button onClick={newSong} className='p-auto border mt-auto rounded py-4 mb-3'>New song</button>
        </div>
        <div className="flex-[6] flex flex-col hover:cursor-pointer" onClick={togglePlay}>
          <Lrc
            lrc={data.lrc}
            lineRenderer={lineRenderer}
            verticalSpace
            currentMillisecond={audioRef.current ? audioRef.current.currentTime*1000 : 0}
            recoverAutoScrollInterval={5000}
            recoverAutoScrollSingal={signal}
          />
        <audio controls className='w-full h-40 mt-auto' ref={audioRef} src={`${serverUrl}${curTrack}`}/>
        </div>
      </div>
    </>
  )
}

export default Sing