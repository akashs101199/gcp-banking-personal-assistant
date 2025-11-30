import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, X, Activity, MessageSquare, Send, Headphones } from 'lucide-react';
import clsx from 'clsx';

const VoiceChat = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [isConnected, setIsConnected] = useState(false);
    const [isHandsFree, setIsHandsFree] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');

    const websocketRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const audioContextRef = useRef(null);
    const canvasRef = useRef(null);
    const animationFrameRef = useRef(null);
    const analyserRef = useRef(null);
    const messagesEndRef = useRef(null);
    const silenceStartRef = useRef(null);

    const API_KEY = import.meta.env.VITE_API_KEY;
    const WS_URL = import.meta.env.VITE_WS_URL;

    useEffect(() => {
        return () => {
            stopRecording();
            if (websocketRef.current) {
                websocketRef.current.close();
            }
            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }
        };
    }, []);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const connectWebSocket = () => {
        console.log('Attempting to connect WebSocket...', {
            readyState: websocketRef.current?.readyState,
            isConnected
        });

        if (websocketRef.current?.readyState === WebSocket.OPEN || websocketRef.current?.readyState === WebSocket.CONNECTING) {
            console.log('WebSocket already open or connecting, skipping connection');
            return;
        }

        const ws = new WebSocket(`${WS_URL}?key=${API_KEY}`);

        ws.onopen = () => {
            console.log('Connected to Voice Agent');
            setIsConnected(true);
            addMessage('system', 'Connected to Banking Assistant');
        };

        ws.onclose = () => {
            console.log('Disconnected from Voice Agent');
            setIsConnected(false);
            setIsRecording(false);
            addMessage('system', 'Disconnected');
        };

        ws.onmessage = async (event) => {
            if (event.data instanceof Blob) {
                playAudioResponse(event.data);
            } else {
                try {
                    const data = JSON.parse(event.data);

                    // Handle audio if present
                    if (data.audio) {
                        const audioBytes = Uint8Array.from(atob(data.audio), c => c.charCodeAt(0));
                        const audioBlob = new Blob([audioBytes], { type: 'audio/wav' }); // Assuming WAV/Linear16
                        playAudioResponse(audioBlob);
                    }

                    if (data.text && data.type !== 'transcript') {
                        addMessage('agent', data.text);
                    } else if (data.type === 'transcript') {
                        addMessage('user', data.text);
                    } else if (data.type === 'text_response') {
                        addMessage('agent', data.text);
                    }
                } catch (e) {
                    addMessage('agent', event.data);
                }
            }
        };

        websocketRef.current = ws;
    };

    const startRecording = async () => {
        try {
            if (!isConnected) connectWebSocket();

            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true
                }
            });

            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioContextRef.current.createMediaStreamSource(stream);
            analyserRef.current = audioContextRef.current.createAnalyser();
            analyserRef.current.fftSize = 256;
            source.connect(analyserRef.current);

            drawVisualizer();

            const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
            mediaRecorderRef.current = mediaRecorder;

            const chunks = [];
            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    chunks.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                if (websocketRef.current?.readyState === WebSocket.OPEN && chunks.length > 0) {
                    const blob = new Blob(chunks, { type: 'audio/webm' });
                    websocketRef.current.send(blob);
                    chunks.length = 0; // Clear chunks
                }
            };

            mediaRecorder.start(100);
            setIsRecording(true);
            addMessage('system', isHandsFree ? 'Hands-free mode active. Listening...' : 'Listening...');

        } catch (err) {
            console.error('Error accessing microphone:', err);
            addMessage('system', 'Error accessing microphone');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
            setIsRecording(false);

            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }

            const canvas = canvasRef.current;
            if (canvas) {
                const ctx = canvas.getContext('2d');
                ctx.clearRect(0, 0, canvas.width, canvas.height);
            }
        }
    };

    const toggleRecording = () => {
        if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    };

    const audioQueueRef = useRef([]);
    const isPlayingRef = useRef(false);
    const currentAudioRef = useRef(null);

    const processQueue = async () => {
        if (isPlayingRef.current || audioQueueRef.current.length === 0) return;

        isPlayingRef.current = true;
        const blob = audioQueueRef.current.shift();
        const audioUrl = URL.createObjectURL(blob);
        const audio = new Audio(audioUrl);
        currentAudioRef.current = audio;

        audio.onended = () => {
            URL.revokeObjectURL(audioUrl);
            isPlayingRef.current = false;
            currentAudioRef.current = null;
            processQueue(); // Play next chunk
        };

        try {
            await audio.play();
        } catch (err) {
            console.error('Error playing audio:', err);
            isPlayingRef.current = false;
            processQueue();
        }
    };

    const playAudioResponse = (blob) => {
        audioQueueRef.current.push(blob);
        processQueue();
    };

    const stopAudioPlayback = () => {
        audioQueueRef.current = []; // Clear queue
        if (currentAudioRef.current) {
            currentAudioRef.current.pause();
            currentAudioRef.current = null;
        }
        isPlayingRef.current = false;
    };

    const handleSendMessage = () => {
        if (!inputText.trim()) return;

        if (!isConnected) connectWebSocket();

        // Wait for connection if not ready
        if (websocketRef.current?.readyState !== WebSocket.OPEN) {
            // Simple retry logic or just wait (in real app, use queue)
            setTimeout(() => handleSendMessage(), 500);
            return;
        }

        const message = { text: inputText };
        websocketRef.current.send(JSON.stringify(message));
        addMessage('user', inputText);
        setInputText('');
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    const drawVisualizer = () => {
        if (!analyserRef.current || !canvasRef.current) return;

        const bufferLength = analyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        const canvas = canvasRef.current;
        const ctx = canvas.getContext('2d');
        const width = canvas.width;
        const height = canvas.height;

        const draw = () => {
            animationFrameRef.current = requestAnimationFrame(draw);
            analyserRef.current.getByteFrequencyData(dataArray);

            // Clear the canvas
            ctx.clearRect(0, 0, width, height);

            // Circular Wave Visualizer
            const centerX = width / 2;
            const centerY = height / 2;
            const radius = Math.min(width, height) / 3;

            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#e5e7eb'; // Base circle (gray-200)
            ctx.lineWidth = 2;
            ctx.stroke();

            // Draw frequency bars around the circle
            const barCount = 60; // Fewer bars for cleaner look
            const step = Math.floor(bufferLength / barCount);

            for (let i = 0; i < barCount; i++) {
                const value = dataArray[i * step];
                const percent = value / 255;
                const barHeight = radius * 0.5 * percent;
                const angle = (i / barCount) * 2 * Math.PI;

                const x1 = centerX + Math.cos(angle) * radius;
                const y1 = centerY + Math.sin(angle) * radius;
                const x2 = centerX + Math.cos(angle) * (radius + barHeight);
                const y2 = centerY + Math.sin(angle) * (radius + barHeight);

                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.strokeStyle = `hsl(${210 + percent * 60}, 100%, 50%)`; // Blue to Purple
                ctx.lineWidth = 4;
                ctx.lineCap = 'round';
                ctx.stroke();
            }

            // VAD Logic: Calculate average volume
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;

            if (isHandsFree && isRecording) {
                if (average > 25) { // Threshold for speech
                    silenceStartRef.current = null;

                    // BARGE-IN: If user speaks, stop AI playback immediately
                    if (audioQueueRef.current.length > 0 || isPlayingRef.current) {
                        console.log('Barge-in detected! Stopping AI playback.');
                        stopAudioPlayback();
                        // Clear backend queue (optional, requires new message type)
                        websocketRef.current.send(JSON.stringify({ type: "interrupt" }));
                    }

                } else {
                    if (!silenceStartRef.current) {
                        silenceStartRef.current = Date.now();
                    } else if (Date.now() - silenceStartRef.current > 600) { // 0.6s silence
                        console.log('Silence detected, sending audio...');
                        stopRecording(); // This sends the blob
                        silenceStartRef.current = null;

                        // Immediately restart recording for next turn (Full Duplex)
                        setTimeout(() => startRecording(), 100);
                    }
                }
            }
        };

        draw();
    };

    const addMessage = (sender, text) => {
        setMessages(prev => {
            const lastMsg = prev[prev.length - 1];
            // If last message is from same sender (and not system), append to it
            if (lastMsg && lastMsg.sender === sender && sender !== 'system') {
                const updated = [...prev];
                updated[updated.length - 1] = { ...lastMsg, text: lastMsg.text + " " + text };
                return updated;
            }
            return [...prev, { sender, text, time: new Date().toLocaleTimeString() }];
        });
    };

    const toggleChat = () => {
        setIsOpen(!isOpen);
        if (!isOpen && !isConnected) {
            connectWebSocket();
        }
    };

    return (
        <div className="fixed bottom-6 right-6 z-50">
            {isOpen && (
                <div className="mb-4 w-96 bg-white rounded-2xl shadow-2xl border border-secondary-200 overflow-hidden flex flex-col animate-in slide-in-from-bottom-5 fade-in duration-300 h-[500px]">
                    {/* Header */}
                    <div className="bg-brand-900 p-4 flex justify-between items-center text-white shrink-0">
                        <div className="flex items-center gap-2">
                            <Activity size={18} className={isConnected ? "text-green-400" : "text-red-400"} />
                            <span className="font-semibold">Banking Assistant</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setIsHandsFree(!isHandsFree)}
                                className={clsx("p-1.5 rounded transition-colors", isHandsFree ? "bg-brand-700 text-white" : "text-brand-300 hover:text-white")}
                                title="Hands-Free Mode"
                            >
                                <Headphones size={18} />
                            </button>
                            <button onClick={() => setIsOpen(false)} className="hover:bg-brand-800 p-1 rounded">
                                <X size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Visualizer (Only visible when recording) */}
                    <div className={clsx("bg-secondary-900 relative transition-all duration-300", isRecording ? "h-24" : "h-0")}>
                        <canvas ref={canvasRef} width="384" height="96" className="w-full h-full opacity-80" />
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-secondary-50">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={clsx(
                                "p-3 rounded-xl text-sm max-w-[85%] shadow-sm",
                                msg.sender === 'agent' ? "bg-white border border-secondary-200 self-start text-secondary-800" :
                                    msg.sender === 'user' ? "bg-brand-600 text-white self-end ml-auto" :
                                        "bg-transparent text-center text-xs text-secondary-400 w-full italic shadow-none"
                            )}>
                                {msg.text}
                            </div>
                        ))}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-3 bg-white border-t border-secondary-200 shrink-0">
                        <div className="flex items-center gap-2">
                            <button
                                onClick={toggleRecording}
                                className={clsx(
                                    "p-3 rounded-full transition-all shadow-sm shrink-0",
                                    isRecording
                                        ? "bg-red-100 text-red-600 hover:bg-red-200"
                                        : "bg-secondary-100 text-secondary-600 hover:bg-secondary-200"
                                )}
                            >
                                {isRecording ? <MicOff size={20} /> : <Mic size={20} />}
                            </button>

                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder={isRecording ? "Listening..." : "Type a message..."}
                                    className="w-full pl-4 pr-10 py-2.5 bg-secondary-50 border border-secondary-200 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                                    disabled={isRecording && !isHandsFree} // Optional: disable text input while recording unless hands-free
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!inputText.trim()}
                                    className="absolute right-1.5 top-1.5 p-1.5 bg-brand-600 text-white rounded-full hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    <Send size={14} />
                                </button>
                            </div>
                        </div>
                        {isHandsFree && (
                            <div className="text-center mt-2">
                                <span className="text-xs text-brand-600 font-medium px-2 py-1 bg-brand-50 rounded-full border border-brand-100">
                                    Hands-Free Mode Active
                                </span>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* FAB */}
            {!isOpen && (
                <button
                    onClick={toggleChat}
                    className="p-4 bg-brand-600 text-white rounded-full shadow-xl hover:bg-brand-700 transition-all hover:scale-105"
                >
                    <MessageSquare size={24} />
                </button>
            )}
        </div>
    );
};

export default VoiceChat;
