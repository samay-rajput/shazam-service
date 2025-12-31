import { useState, useRef, useEffect } from "react";

const MicIcon = () => (
  <svg
    width="48"
    height="48"
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-hidden="true"
    focusable="false"
  >
    <path d="M12 14a3 3 0 0 0 3-3V5a3 3 0 1 0-6 0v6a3 3 0 0 0 3 3Zm5-3a1 1 0 1 1 2 0 7 7 0 0 1-6 6.93V21h3a1 1 0 1 1 0 2H8a1 1 0 1 1 0-2h3v-3.07A7 7 0 0 1 5 11a1 1 0 0 1 2 0 5 5 0 0 0 10 0Z" />
  </svg>
);

const LogoIcon = () => (
  <svg
    width="28"
    height="28"
    viewBox="0 0 24 24"
    fill="currentColor"
    aria-hidden="true"
    focusable="false"
  >
    <path d="M9 3v12.17A3 3 0 1 0 11 18V8h5v6.17A3 3 0 1 0 18 16V3H9Z" />
  </svg>
);

function App() {
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [recordingTime, setRecordingTime] = useState(0);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timeoutRef = useRef(null);
  const streamRef = useRef(null);
  const cancelledRef = useRef(false);
  const intervalRef = useRef(null);

  // Recording timer
  useEffect(() => {
    if (isRecording) {
      setRecordingTime(0);
      intervalRef.current = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(intervalRef.current);
      setRecordingTime(0);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRecording]);

  // START RECORDING
  const startRecording = async () => {
    setError(null);
    setResult(null);
    cancelledRef.current = false;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        if (cancelledRef.current || audioChunksRef.current.length === 0) return;

        const audioBlob = new Blob(audioChunksRef.current, {
          type: "audio/webm",
        });

        const audioFile = new File([audioBlob], "recording.webm", {
          type: "audio/webm",
        });

        await identifySong(audioFile);
      };

      mediaRecorder.start();
      setIsRecording(true);

      timeoutRef.current = setTimeout(() => {
        stopRecording(false);
      }, 15000);
    } catch (err) {
      console.error("Microphone error:", err);
      setError("Microphone access denied. Please allow microphone permissions.");
    }
  };

  const stopRecording = (isCancel) => {
    clearTimeout(timeoutRef.current);

    if (isCancel) {
      cancelledRef.current = true;
      audioChunksRef.current = [];
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    setIsRecording(false);
  };

  const identifySong = async (file) => {
    setIsLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("https://echoid-backend-ad59.onrender.com/identify", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (data.status === "No Match") {
        setError(data.reason || "No match found");
        setResult(null);
      } else {
        setResult(data);
        setError(null);
      }
    } catch (err) {
      console.error("Identification error:", err);
      setError("Failed to identify song. Please try again.");
    }

    setIsLoading(false);
  };

  const resetState = () => {
    setResult(null);
    setError(null);
  };

  // Sound wave bars component
  const SoundWave = () => (
    <div style={styles.soundWave}>
      {[...Array(5)].map((_, i) => (
        <div
          key={i}
          style={{
            ...styles.soundBar,
            animationDelay: `${i * 0.1}s`,
          }}
        />
      ))}
    </div>
  );

  return (
    <div style={styles.page}>
      {/* Animated background orbs + grid */}
      <div style={styles.bgGrid}></div>
      <div style={styles.bgOrb1}></div>
      <div style={styles.bgOrb2}></div>
      <div style={styles.bgOrb3}></div>

      <div style={styles.container}>
        {/* Header */}
        <header style={styles.header}>
          <div style={styles.logoContainer}>
            <div style={styles.logoWrapper}>
              <span style={styles.logoIcon} aria-hidden="true">
                <LogoIcon />
              </span>
            </div>
            <div>
              <h1 style={styles.title}>EchoID</h1>
              <p style={styles.tagline}>Audio Recognition</p>
            </div>
          </div>
          <p style={styles.subtitle}>
            Identify any song playing around you
          </p>
          <div style={styles.headerAccent}></div>
        </header>

        {/* Main Content */}
        <main style={styles.main}>
          {/* Idle State */}
          {!isRecording && !isLoading && !result && !error && (
            <div style={styles.identifySection}>
              <div style={styles.buttonGlow}></div>
              <button onClick={startRecording} style={styles.identifyButton}>
                <div style={styles.buttonInner}>
                  <span style={styles.buttonIcon} aria-hidden="true">
                    <MicIcon />
                  </span>
                  <span style={styles.buttonText}>Tap to Identify</span>
                </div>
              </button>
              <p style={styles.hint}>
                <span style={styles.hintIcon}>⏱</span>
                Recording stops after 15 seconds
              </p>
            </div>
          )}

          {/* Recording State */}
          {isRecording && (
            <div style={styles.recordingSection}>
              <div style={styles.recordingVisual}>
                <div style={styles.pulseRing1}></div>
                <div style={styles.pulseRing2}></div>
                <div style={styles.pulseRing3}></div>
                <div style={styles.pulseCore}>
                  <SoundWave />
                </div>
              </div>
              <div style={styles.recordingInfo}>
                <p style={styles.listeningText}>Listening...</p>
                <p style={styles.timer}>{recordingTime}s / 15s</p>
                <div style={styles.progressBar}>
                  <div
                    style={{
                      ...styles.progressFill,
                      width: `${(recordingTime / 15) * 100}%`,
                    }}
                  ></div>
                </div>
              </div>
              <button
                onClick={() => stopRecording(true)}
                style={styles.cancelButton}
              >
                <span>✕</span> Cancel
              </button>
            </div>
          )}

          {/* Loading State */}
          {isLoading && (
            <div style={styles.loadingSection}>
              <div style={styles.loaderContainer}>
                <div style={styles.loader}>
                  <div style={styles.loaderInner}></div>
                </div>
                <div style={styles.loaderIcon}>🔍</div>
              </div>
              <p style={styles.loadingText}>Analyzing audio...</p>
              <p style={styles.loadingSubtext}>Matching against database</p>
            </div>
          )}

          {/* Error State */}
          {error && !isRecording && !isLoading && (
            <div style={styles.errorSection}>
              <div style={styles.errorIconWrapper}>
                <span style={styles.errorIconInner}>!</span>
              </div>
              <h3 style={styles.errorTitle}>No Match Found</h3>
              <p style={styles.errorText}>{error}</p>
              <button onClick={resetState} style={styles.tryAgainButton}>
                <span>🔄</span> Try Again
              </button>
            </div>
          )}

          {/* Result State */}
          {result && !isRecording && !isLoading && (
            <div style={styles.resultSection}>
              <div style={styles.matchBadge}>
                <span>✓</span> Match Found!
              </div>
              <div style={styles.resultCard}>
                <div style={styles.coverArtWrapper}>
                  <img
                    src={result.cover_art}
                    alt={`${result.title} cover art`}
                    style={styles.coverArt}
                  />
                  <div style={styles.coverOverlay}></div>
                  <div style={styles.playBadge}>
                    <span>▶</span>
                  </div>
                </div>
                <div style={styles.songDetails}>
                  <h2 style={styles.songTitle}>{result.title}</h2>
                  <p style={styles.artistName}>
                    <span style={styles.artistIcon}>👤</span>
                    {result.artist}
                  </p>
                  <p style={styles.albumName}>
                    <span style={styles.albumIcon}>💿</span>
                    {result.album_name}
                  </p>
                  {/* <div style={styles.metaChips}>
                    <span style={styles.metaChip}>HQ Match</span>
                    <span style={styles.metaChip}>15s Sample</span>
                  </div> */}
                </div>
                <a
                  href={result.spotify_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.spotifyButton}
                >
                  <svg style={styles.spotifySvg} viewBox="0 0 24 24">
                    <path
                      fill="currentColor"
                      d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"
                    />
                  </svg>
                  Play on Spotify
                </a>
              </div>
              <button onClick={resetState} style={styles.newSearchButton}>
                <span>🎤</span> Identify Another Song
              </button>
            </div>
          )}
        </main>

        {/* Footer */}
        <footer style={styles.footer}>
          <div style={styles.footerContent}>
            <span style={styles.footerIcon}>⚡</span>
            <span>Powered by Audio Fingerprinting</span>
          </div>
        </footer>
      </div>

      {/* CSS Animations + Responsive tokens */}
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {
          --size-cover: 220px;
          --container-width: 520px;
          --title-size: 32px;
          --button-size: 180px;
          --card-padding: 32px;
          --container-padding: 50px 24px;
        }
        @media (max-width: 360px) {
          :root {
            --size-cover: 180px;
            --container-width: 320px;
            --title-size: 30px;
            --button-size: 150px;
            --card-padding: 26px;
            --container-padding: 40px 16px;
          }
        }
        @media (min-width: 768px) {
          :root {
            --size-cover: 260px;
            --container-width: 640px;
            --title-size: 36px;
            --button-size: 200px;
            --card-padding: 36px;
            --container-padding: 60px 28px;
          }
        }
        @media (min-width: 1024px) {
          :root {
            --size-cover: 280px;
            --container-width: 720px;
            --title-size: 38px;
            --button-size: 220px;
            --card-padding: 40px;
            --container-padding: 70px 32px;
          }
        }
        @media (min-width: 1440px) {
          :root {
            --size-cover: 320px;
            --container-width: 820px;
            --title-size: 42px;
            --button-size: 240px;
            --card-padding: 46px;
            --container-padding: 80px 36px;
          }
        }
        @keyframes pulse1 {
          0%, 100% { transform: scale(1); opacity: 0.6; }
          50% { transform: scale(1.5); opacity: 0; }
        }
        @keyframes pulse2 {
          0%, 100% { transform: scale(1); opacity: 0.4; }
          50% { transform: scale(1.8); opacity: 0; }
        }
        @keyframes pulse3 {
          0%, 100% { transform: scale(1); opacity: 0.2; }
          50% { transform: scale(2.1); opacity: 0; }
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        @keyframes glow {
          0%, 100% { opacity: 0.5; transform: scale(1); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
        @keyframes soundBar {
          0%, 100% { height: 8px; }
          50% { height: 32px; }
        }
        @keyframes orbFloat1 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(30px, -50px); }
          66% { transform: translate(-20px, 20px); }
        }
        @keyframes orbFloat2 {
          0%, 100% { transform: translate(0, 0); }
          33% { transform: translate(-40px, 30px); }
          66% { transform: translate(50px, -30px); }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
        button:hover {
          transform: scale(1.02);
        }
        button:active {
          transform: scale(0.98);
        }
      `}</style>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "linear-gradient(145deg, #0d0d0d 0%, #1a1a1a 50%, #141414 100%)",
    fontFamily: "'Manrope', 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif",
    WebkitFontSmoothing: "antialiased",
    MozOsxFontSmoothing: "grayscale",
    position: "relative",
    overflow: "hidden",
  },
  bgGrid: {
    position: "absolute",
    inset: 0,
    backgroundImage: "radial-gradient(circle at 1px 1px, rgba(255,255,255,0.03) 1px, transparent 0)",
    backgroundSize: "40px 40px",
    opacity: 0.6,
    pointerEvents: "none",
  },
  bgOrb1: {
    position: "absolute",
    width: "400px",
    height: "400px",
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, transparent 70%)",
    top: "-150px",
    right: "-150px",
    animation: "orbFloat1 20s ease-in-out infinite",
    pointerEvents: "none",
  },
  bgOrb2: {
    position: "absolute",
    width: "350px",
    height: "350px",
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(236, 72, 153, 0.06) 0%, transparent 70%)",
    bottom: "5%",
    left: "-100px",
    animation: "orbFloat2 25s ease-in-out infinite",
    pointerEvents: "none",
  },
  bgOrb3: {
    position: "absolute",
    width: "250px",
    height: "250px",
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(34, 197, 94, 0.06) 0%, transparent 70%)",
    top: "50%",
    right: "5%",
    animation: "orbFloat1 15s ease-in-out infinite reverse",
    pointerEvents: "none",
  },
  container: {
    maxWidth: "var(--container-width)",
    margin: "0 auto",
    padding: "var(--container-padding)",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    position: "relative",
    zIndex: 1,
  },
  header: {
    textAlign: "center",
    marginBottom: "50px",
    animation: "fadeInUp 0.6s ease-out",
  },
  logoContainer: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "16px",
    marginBottom: "20px",
  },
  logoWrapper: {
    width: "52px",
    height: "52px",
    borderRadius: "14px",
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 4px 12px rgba(99, 102, 241, 0.25)",
  },
  logoIcon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "28px",
    height: "28px",
    color: "#fff",
    userSelect: "none",
    WebkitUserSelect: "none",
    MozUserSelect: "none",
  },
  title: {
    color: "#fff",
    fontSize: "var(--title-size)",
    fontWeight: "800",
    margin: 0,
    letterSpacing: "-1px",
    textAlign: "left",
  },
  tagline: {
    color: "#a78bfa",
    fontSize: "12px",
    margin: 0,
    fontWeight: "500",
    textTransform: "uppercase",
    letterSpacing: "2px",
    textAlign: "left",
  },
  subtitle: {
    color: "#71717a",
    fontSize: "15px",
    margin: 0,
    fontWeight: "400",
  },
  main: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
  },
  identifySection: {
    textAlign: "center",
    animation: "fadeInUp 0.6s ease-out 0.2s both",
    position: "relative",
  },
  buttonGlow: {
    position: "absolute",
    width: "180px",
    height: "180px",
    borderRadius: "50%",
    background: "radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 70%)",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    animation: "glow 4s ease-in-out infinite",
    pointerEvents: "none",
  },
  identifyButton: {
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    border: "none",
    borderRadius: "50%",
    width: "var(--button-size)",
    height: "var(--button-size)",
    cursor: "pointer",
    padding: "4px",
    boxShadow: "0 8px 24px rgba(99, 102, 241, 0.3)",
    transition: "all 0.3s ease",
    position: "relative",
    userSelect: "none",
    WebkitUserSelect: "none",
    MozUserSelect: "none",
  },
  buttonInner: {
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    background: "linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 100%)",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
    userSelect: "none",
    WebkitUserSelect: "none",
    MozUserSelect: "none",
  },
  buttonIcon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: "52px",
    height: "52px",
    color: "#fff",
    userSelect: "none",
    WebkitUserSelect: "none",
    MozUserSelect: "none",
  },
  buttonText: {
    color: "#fff",
    fontSize: "13px",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "1px",
    userSelect: "none",
    WebkitUserSelect: "none",
    MozUserSelect: "none",
  },
  hint: {
    color: "#52525b",
    fontSize: "13px",
    marginTop: "28px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
  },
  hintIcon: {
    fontSize: "14px",
  },
  recordingSection: {
    textAlign: "center",
    animation: "fadeInUp 0.4s ease-out",
  },
  recordingVisual: {
    position: "relative",
    width: "160px",
    height: "160px",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    margin: "0 auto",
  },
  pulseRing1: {
    position: "absolute",
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    border: "1.5px solid rgba(239, 68, 68, 0.4)",
    animation: "pulse1 2s ease-out infinite",
  },
  pulseRing2: {
    position: "absolute",
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    border: "1.5px solid rgba(239, 68, 68, 0.25)",
    animation: "pulse2 2s ease-out infinite 0.3s",
  },
  pulseRing3: {
    position: "absolute",
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    border: "1.5px solid rgba(239, 68, 68, 0.1)",
    animation: "pulse3 2s ease-out infinite 0.6s",
  },
  pulseCore: {
    width: "100px",
    height: "100px",
    borderRadius: "50%",
    background: "linear-gradient(135deg, #ef4444 0%, #dc2626 100%)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 8px 24px rgba(239, 68, 68, 0.3)",
    zIndex: 1,
  },
  soundWave: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "5px",
    height: "36px",
  },
  soundBar: {
    width: "5px",
    height: "8px",
    background: "#fff",
    borderRadius: "2px",
    animation: "soundBar 0.8s ease-in-out infinite",
  },
  recordingInfo: {
    marginTop: "24px",
  },
  listeningText: {
    color: "#fff",
    fontSize: "22px",
    fontWeight: "600",
    margin: "0 0 8px 0",
  },
  timer: {
    color: "#ef4444",
    fontSize: "15px",
    fontWeight: "500",
    margin: "0 0 16px 0",
  },
  progressBar: {
    width: "180px",
    height: "4px",
    background: "rgba(255,255,255,0.08)",
    borderRadius: "2px",
    margin: "0 auto",
    overflow: "hidden",
  },
  progressFill: {
    height: "100%",
    background: "linear-gradient(90deg, #ef4444, #f97316)",
    borderRadius: "2px",
    transition: "width 1s linear",
  },
  cancelButton: {
    marginTop: "28px",
    background: "transparent",
    border: "1.5px solid rgba(239, 68, 68, 0.5)",
    borderRadius: "50px",
    padding: "12px 32px",
    color: "#ef4444",
    fontSize: "14px",
    fontWeight: "500",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    transition: "all 0.2s",
  },
  loadingSection: {
    textAlign: "center",
    animation: "fadeInUp 0.4s ease-out",
  },
  loaderContainer: {
    position: "relative",
    width: "80px",
    height: "80px",
    margin: "0 auto 24px",
  },
  loader: {
    width: "100%",
    height: "100%",
    borderRadius: "50%",
    border: "2px solid rgba(99, 102, 241, 0.15)",
    borderTopColor: "#6366f1",
    animation: "spin 1s linear infinite",
  },
  loaderInner: {
    position: "absolute",
    top: "8px",
    left: "8px",
    right: "8px",
    bottom: "8px",
    borderRadius: "50%",
    border: "2px solid rgba(139, 92, 246, 0.15)",
    borderBottomColor: "#8b5cf6",
    animation: "spin 1.5s linear infinite reverse",
  },
  loaderIcon: {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    fontSize: "24px",
  },
  loadingText: {
    color: "#fff",
    fontSize: "18px",
    fontWeight: "500",
    margin: "0 0 6px 0",
  },
  loadingSubtext: {
    color: "#71717a",
    fontSize: "13px",
    margin: 0,
  },
  errorSection: {
    textAlign: "center",
    animation: "fadeInUp 0.4s ease-out",
  },
  errorIconWrapper: {
    width: "72px",
    height: "72px",
    borderRadius: "50%",
    background: "rgba(239, 68, 68, 0.1)",
    border: "1.5px solid rgba(239, 68, 68, 0.2)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    margin: "0 auto 20px",
  },
  errorIconInner: {
    fontSize: "32px",
    fontWeight: "600",
    color: "#ef4444",
  },
  errorTitle: {
    color: "#fff",
    fontSize: "20px",
    fontWeight: "600",
    margin: "0 0 10px 0",
  },
  errorText: {
    color: "#71717a",
    fontSize: "14px",
    margin: "0 0 24px 0",
    maxWidth: "280px",
    lineHeight: "1.5",
  },
  tryAgainButton: {
    background: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    border: "none",
    borderRadius: "50px",
    padding: "14px 36px",
    color: "#fff",
    fontSize: "15px",
    fontWeight: "500",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "10px",
    boxShadow: "0 4px 16px rgba(99, 102, 241, 0.25)",
    transition: "all 0.2s",
  },
  resultSection: {
    textAlign: "center",
    width: "100%",
    animation: "fadeInUp 0.5s ease-out",
  },
  matchBadge: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    background: "rgba(34, 197, 94, 0.1)",
    border: "1px solid rgba(34, 197, 94, 0.2)",
    borderRadius: "50px",
    padding: "8px 18px",
    color: "#22c55e",
    fontSize: "13px",
    fontWeight: "500",
    marginBottom: "24px",
  },
  resultCard: {
    background: "rgba(255, 255, 255, 0.03)",
    backdropFilter: "blur(16px)",
    borderRadius: "24px",
    padding: "var(--card-padding)",
    border: "1px solid rgba(255, 255, 255, 0.06)",
    boxShadow: "0 16px 48px rgba(0, 0, 0, 0.3)",
  },
  coverArtWrapper: {
    position: "relative",
    display: "inline-block",
    marginBottom: "24px",
  },
  coverArt: {
    width: "var(--size-cover)",
    height: "var(--size-cover)",
    borderRadius: "16px",
    objectFit: "cover",
    boxShadow: "0 12px 40px rgba(0, 0, 0, 0.4)",
  },
  coverOverlay: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    borderRadius: "16px",
    background: "linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.3) 100%)",
    pointerEvents: "none",
  },
  playBadge: {
    position: "absolute",
    bottom: "-10px",
    right: "-10px",
    width: "46px",
    height: "46px",
    background: "#1DB954",
    borderRadius: "50%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "18px",
    color: "#fff",
    boxShadow: "0 4px 12px rgba(29, 185, 84, 0.3)",
    border: "3px solid #1a1a1a",
  },
  songDetails: {
    color: "#fff",
    marginBottom: "20px",
  },
  songTitle: {
    fontSize: "calc(var(--title-size) - 6px)",
    fontWeight: "700",
    margin: "0 0 14px 0",
    lineHeight: "1.2",
    letterSpacing: "-0.5px",
    color: "#fff",
  },
  artistName: {
    fontSize: "16px",
    color: "#a78bfa",
    margin: "0 0 6px 0",
    fontWeight: "500",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
  },
  artistIcon: {
    fontSize: "13px",
    opacity: 0.7,
  },
  albumName: {
    fontSize: "13px",
    color: "#71717a",
    margin: 0,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "8px",
  },
  albumIcon: {
    fontSize: "13px",
    opacity: 0.7,
  },
  spotifyButton: {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    gap: "10px",
    background: "#1DB954",
    color: "#fff",
    textDecoration: "none",
    padding: "14px 28px",
    borderRadius: "50px",
    fontSize: "15px",
    fontWeight: "600",
    transition: "all 0.2s",
    boxShadow: "0 4px 16px rgba(29, 185, 84, 0.25)",
    width: "100%",
    marginTop: "8px",
  },
  spotifySvg: {
    width: "22px",
    height: "22px",
  },
  newSearchButton: {
    marginTop: "20px",
    background: "transparent",
    border: "1.5px solid rgba(255, 255, 255, 0.15)",
    borderRadius: "50px",
    padding: "12px 28px",
    color: "#a1a1aa",
    fontSize: "14px",
    fontWeight: "500",
    cursor: "pointer",
    display: "inline-flex",
    alignItems: "center",
    gap: "10px",
    transition: "all 0.2s",
  },
  footer: {
    textAlign: "center",
    marginTop: "auto",
    paddingTop: "32px",
  },
  footerContent: {
    display: "inline-flex",
    alignItems: "center",
    gap: "8px",
    color: "#52525b",
    fontSize: "12px",
    padding: "10px 18px",
    background: "rgba(255,255,255,0.02)",
    borderRadius: "50px",
    border: "1px solid rgba(255,255,255,0.04)",
  },
  footerIcon: {
    fontSize: "12px",
  },
  headerAccent: {
    margin: "16px auto 0",
    width: "100px",
    height: "3px",
    borderRadius: "999px",
    background: "linear-gradient(90deg, #6366f1, #22c55e, #8b5cf6)",
    opacity: 0.6,
  },
  metaChips: {
    display: "flex",
    gap: "10px",
    justifyContent: "center",
    marginTop: "14px",
    flexWrap: "wrap",
  },
  metaChip: {
    padding: "6px 12px",
    borderRadius: "999px",
    border: "1px solid rgba(255,255,255,0.06)",
    background: "rgba(255,255,255,0.02)",
    color: "#71717a",
    fontSize: "11px",
    letterSpacing: "0.5px",
    textTransform: "uppercase",
  },
};

export default App;
