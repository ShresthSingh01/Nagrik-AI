/**
 * Nagrik - Voice-First Civic Assistant
 * Nuclear Reset: Cache Busting & Bilingual Fallbacks
 */

// --- DOM Elements ---
const views = {
  login: document.getElementById("view-login"),
  home: document.getElementById("view-home"),
  scan: document.getElementById("view-scan"),
  history: document.getElementById("view-history"),
  memory: document.getElementById("view-memory"),
};

const scanSteps = {
  1: document.getElementById("scan-step-1"),
  2: document.getElementById("scan-step-2"),
  3: document.getElementById("scan-step-3"),
};

const scanLabels = {
  1: document.getElementById("step-1-label"),
  2: document.getElementById("step-2-label"),
  3: document.getElementById("step-3-label"),
};

const navItems = {
  home: document.getElementById("nav-home"),
  scan: document.getElementById("nav-scan"),
  history: document.getElementById("nav-history"),
  memory: document.getElementById("nav-memory"),
};

// Memory Elements
const memorySearchInput = document.getElementById("memorySearchInput");
const memorySearchBtn = document.getElementById("memorySearchBtn");
const memoryResults = document.getElementById("memoryResults");

// Inputs & Buttons
const cameraInput = document.getElementById("cameraInput");
const fileInput = document.getElementById("fileInput");
const processBtn = document.getElementById("processBtn");
const startScanBtn = document.getElementById("startScanBtn");
const takePhotoBtn = document.getElementById("takePhotoBtn");
const uploadFileBtn = document.getElementById("uploadFileBtn");
const cancelStepBtn = document.getElementById("cancelStepBtn");
const newScanShortBtn = document.getElementById("newScanShortBtn");
const logoutBtn = document.getElementById("logoutBtn");
const shareBtn = document.getElementById("shareBtn");

// Result Elements
const overallSummaryEl = document.getElementById("overallSummary");
const pagesContainer = document.getElementById("pagesContainer");
const resultsSection = document.getElementById("resultsSection");
const audioPlayer = document.getElementById("audioPlayer");
const audioController = document.getElementById("audioController");
const confirmFileName = document.getElementById("confirmFileName");
const processingStatus = document.getElementById("processingStatus");

// Activity Lists
const recentActivityList = document.getElementById("recentActivityList");
const historyList = document.getElementById("historyList");

// New UI Elements
const lightweightToggle = document.getElementById("lightweightToggle");
const resultsBackBtn = document.getElementById("resultsBackBtn");
const resFooterBackBtn = document.getElementById("resFooterBackBtn");
const resFooterNextBtn = document.getElementById("resFooterNextBtn");
const resFooterReplayBtn = document.getElementById("resFooterReplayBtn");
const closeAskAIBtn = document.getElementById("closeAskAIBtn");
const voiceMicBtn = document.getElementById("voiceMicBtn");
const micLabel = document.getElementById("micLabel");
const voiceTranscript = document.getElementById("voiceTranscript");
const voiceResponseAudio = document.getElementById("voiceResponseAudio");
const askAIChat = document.getElementById("askAIChat");

// --- Onboarding Elements (Renamed for Reset) ---
const onboardingModal = document.getElementById("nagrikOnboarding");
const saveProfileBtn = document.getElementById("saveProfileBtn");
const onboardingSection1 = document.getElementById("onboardingSection1");
const onboardingSection2 = document.getElementById("onboardingSection2");

const loginSpinner = document.getElementById("loginSpinner");
const loginSuccessEl = document.getElementById("loginSuccess");
const loginErrorEl = document.getElementById("loginError");
const toggleAuthBtn = document.getElementById("toggleAuthBtn");
const toggleMsg = document.getElementById("toggleMsg");
const fullNameGroup = document.getElementById("full-name-group");
const registerNameInput = document.getElementById("register-name");
const loginMobileInput = document.getElementById("login-mobile");
const loginPassInput = document.getElementById("login-pass");
const captchaInput = document.getElementById("captchaInput");
const askAIToggleBtn = document.getElementById("askAIToggleBtn");
const askAIToggleBtnText = document.getElementById("askAIToggleBtnText");

// --- Auth State ---
let isRegisterMode = false;
let currentCaptcha = "";
const LOG_AUTH_KEY = "nagrik_logged_in";

// Audio Controls
const playPauseBtn = document.getElementById("playPauseBtn");
const audioProgress = document.getElementById("audioProgress");
const currentTimeEl = document.getElementById("currentTime");
const durationTimeEl = document.getElementById("durationTime");

// Field Audio Cache
const fieldAudioCache = new Map();
let currentDocContext = "";

// --- Localization System ---
const I18N = {
  en: {
    hero_title: "Help for your documents.",
    hero_welcome: "Welcome Back",
    hero_need_help: "Need help with a new document today?",
    hero_subtext: "Start a new scan or look at your recent documents below. All your data stays on this phone.",
    btn_start_scan: "Start a New Scan",
    recent_activity: "Recent Activity",
    nav_home: "Home",
    nav_scan: "Scan",
    nav_history: "History",
    scan_step_1: "Intake",
    scan_step_2: "Confirm",
    scan_step_3: "Read",
    intake_title: "How would you like to provide the document?",
    btn_take_photo: "Take a Photo",
    btn_upload_file: "Upload PDF / File",
    photo_subtext: "Best for physical forms and letters.",
    upload_subtext: "Use this for downloaded documents.",
    confirm_title: "Start analysis?",
    confirm_subtext: "Check document details before starting.",
    file_label: "File",
    low_data_mode: "Low Data Mode (Save bandwidth)",
    btn_process: "Process",
    btn_cancel: "Go Back",
    summary_title: "Easy Summary",
    audio_label: "Listen to Summary",
    pages_title: "Page-by-Page Help",
    what_to_fill: "What to fill",
    why_it_matters: "Why it matters",
    example: "Example",
    btn_listen: "🔊 Listen",
    btn_listening: "⏳ Voice...",
    important: "Important",
    share_btn: "Share",
    new_scan_btn: "New Scan",
    // Audio player
    btn_play: "Listen",
    btn_pause: "Pause",
    btn_slow: "Slow",
    btn_fast: "Fast",
    // Processing status
    progress_1: "Reading document...",
    progress_2: "Translating to your language...",
    progress_3: "Simplifying government jargon...",
    progress_4: "Matching with civic guidelines...",
    progress_5: "Almost ready...",
    progress_6: "Finalizing your guide...",
    processing_subtext: "This usually takes 10-15 seconds. Please do not close the app.",
    // History
    history_title: "Your Saved Documents",
    history_subtext: "Showing your last 10 scans.",
    empty_state: "No documents yet. Tap \"Start a New Scan\" to begin.",
    // Ask AI
    ask_ai_btn: "Ask AI",
    ask_ai_title: "Ask Nagrik",
    ask_ai_placeholder: "Tap to speak...",
    ask_ai_send: "Send",
    ask_ai_welcome: "Tap the mic and ask your question by voice.",
    ask_ai_thinking: "Thinking...",
    ask_ai_listening: "Listening... Speak now.",
    ask_ai_error: "Network error. Please try again.",
    // Onboarding
    onboarding_title: "Nagrik — Welcome",
    onboarding_lang_prompt: "🌐 Select Language / भाषा चुनें",
    onboarding_level_title: "Comprehension",
    onboarding_level_prompt: "🧠 Select Understanding Level / समझ का स्तर",
    level_normal: "Normal / सामान्य",
    level_normal_desc: "Educated user",
    level_simple: "Simple / आसान",
    level_simple_desc: "Semi-literate",
    level_voice: "Voice-first / बहुत आसान",
    level_voice_desc: "Low literacy",
    btn_save_start: "Save & Start / शुरू करें",
    step_label: "Step",
    res_back: "Back",
    page_info_text: "Fill these details on this page",
    btn_footer_back: "Previous Page",
    btn_footer_next: "Next Page",
    btn_footer_replay: "Listen Again",
    hero_tagline: "This form is for government help.",
    hero_instructions: "Fill the details below correctly. Listen to audio if confused."
  },
  hi: {
    hero_title: "दस्तावेज़ों को समझने में मदद।",
    hero_welcome: "नमस्ते",
    hero_need_help: "क्या आप आज नए दस्तावेज़ में मदद चाहते हैं?",
    hero_subtext: "नया स्कैन शुरू करें या अपने हाल के दस्तावेज़ नीचे देखें। आपका सारा डेटा इस फोन पर रहता है।",
    btn_start_scan: "नया स्कैन शुरू करें",
    recent_activity: "हाल के दस्तावेज़",
    nav_home: "होम",
    nav_scan: "स्कैन करें",
    nav_history: "पुराने दस्तावेज़",
    scan_step_1: "दस्तावेज़ दें",
    scan_step_2: "चेक करें",
    scan_step_3: "पढ़ें",
    intake_title: "दस्तावेज़ कैसे देना चाहेंगे?",
    btn_take_photo: "फोटो खींचें",
    btn_upload_file: "फाइल अपलोड करें",
    photo_subtext: "फॉर्म या पत्र की फोटो के लिए।",
    upload_subtext: "डाउनलोड किए गए दस्तावेज़ के लिए।",
    confirm_title: "विश्लेषण शुरू करें?",
    confirm_subtext: "शुरू करने से पहले दस्तावेज़ की जानकारी चेक कर लें।",
    file_label: "फाइल",
    low_data_mode: "कम डेटा मोड (डेटा बचाएं)",
    btn_process: "शुरू करें",
    btn_cancel: "पीछे जाएं",
    summary_title: "सरल समझ",
    audio_label: "आवाज़ में सुनें",
    pages_title: "हर पेज की मदद",
    what_to_fill: "क्या भरना है",
    why_it_matters: "क्यों भरना है",
    example: "उदाहरण",
    btn_listen: "🔊 आवाज़ में सुनें",
    btn_listening: "⏳ आवाज़...",
    important: "महत्वपूर्ण",
    share_btn: "शेयर करें",
    new_scan_btn: "नया स्कैन",
    // Audio player
    btn_play: "सुनें",
    btn_pause: "रुकें",
    btn_slow: "धीमा",
    btn_fast: "तेज़",
    // Processing status
    progress_1: "दस्तावेज़ पढ़ रहे हैं...",
    progress_2: "आपकी भाषा में बना रहे हैं...",
    progress_3: "सरकारी भाषा आसान कर रहे हैं...",
    progress_4: "ज़रूरी काम देख रहे हैं...",
    progress_5: "लगभग तैयार...",
    progress_6: "आपकी गाइड बना रहे हैं...",
    processing_subtext: "इसमें 10-15 सेकंड लगते हैं। कृपया ऐप बंद न करें।",
    // History
    history_title: "आपके सेव किए दस्तावेज़",
    history_subtext: "आपके पिछले 10 स्कैन।",
    empty_state: "अभी कोई दस्तावेज़ नहीं। \"नया स्कैन शुरू करें\" दबाएं।",
    // Ask AI
    ask_ai_btn: "पूछें",
    ask_ai_title: "नागरिक से पूछें",
    ask_ai_placeholder: "बोलने के लिए दबाएं...",
    ask_ai_send: "भेजें",
    ask_ai_welcome: "माइक दबाएं और अपनी आवाज़ में सवाल पूछें।",
    ask_ai_thinking: "सोच रहे हैं...",
    ask_ai_listening: "सुन रहे हैं... बोलिए।",
    ask_ai_error: "नेटवर्क समस्या। कृपया दोबारा कोशिश करें।",
    // Onboarding
    onboarding_title: "नागरिक — स्वागत है",
    onboarding_lang_prompt: "🌐 भाषा चुनें / Select Language",
    onboarding_level_title: "समझ का स्तर",
    onboarding_level_prompt: "🧠 समझ का स्तर चुनें / Select Level",
    level_normal: "सामान्य / Normal",
    level_normal_desc: "पढ़े-लिखे उपयोगकर्ता",
    level_simple: "आसान / Simple",
    level_simple_desc: "थोड़ा पढ़े-लिखे",
    level_voice: "बहुत आसान / Voice-first",
    level_voice_desc: "आवाज़ से सीखें",
    btn_save_start: "सेव करें और शुरू करें / Save",
    step_label: "स्टेप",
    res_back: "वापस जाएं",
    page_info_text: "इस पेज में आपको ये जानकारी भरनी है",
    btn_footer_back: "पिछला पेज",
    btn_footer_next: "अगला पेज देखें",
    btn_footer_replay: "फिर से सुनें",
    hero_tagline: "यह फ़ॉर्म सरकारी मदद के लिए है।",
    hero_instructions: "नीचे दी गई जानकारी सही भरें। समझ न आए तो आवाज़ में सुनें।"
  }
};

function applyLanguage(lang) {
  const t = I18N[lang] || I18N.hi;
  
  // Set global storage for logic
  localStorage.setItem("nagrik_lang", lang);
  
  const locMap = {
    "brand-title": t.hero_title,
    "hero-welcome": t.hero_welcome,
    "hero-need-help": t.hero_need_help,
    "hero-subtext": t.hero_subtext,
    "startScanBtn": t.btn_start_scan,
    "recent-activity-label": t.recent_activity,
    "nav-home-label": t.nav_home,
    "nav-scan-label": t.nav_scan,
    "nav-history-label": t.nav_history,
    "step-1-label-text": t.scan_step_1,
    "step-2-label-text": t.scan_step_2,
    "step-3-label-text": t.scan_step_3,
    "intake-title": t.intake_title,
    "take-photo-text": t.btn_take_photo,
    "upload-file-text": t.btn_upload_file,
    "photo-subtext": t.photo_subtext,
    "upload-subtext": t.upload_subtext,
    "confirm-title-el": t.confirm_title,
    "confirm-subtext-el": t.confirm_subtext,
    "file-label-el": t.file_label,
    "lightweight-label": t.low_data_mode,
    "processBtn": t.btn_process,
    "cancelStepBtn": t.btn_cancel,
    "summary-title-el": t.summary_title,
    "audio-label-el": t.audio_label,
    "pages-title-el": t.pages_title,
    "res-back-label": t.res_back,
    "res-current-lang": lang === "hi" ? "हिंदी" : "English",
    "history-title-el": t.history_title,
    "history-subtext-el": t.history_subtext,
    "empty-state-text": t.empty_state,
    "askAIToggleBtnText": t.ask_ai_btn,
    "ask-ai-title-el": t.ask_ai_title,
    "ask-ai-welcome-msg": t.ask_ai_welcome,
    "onboarding-level-title-el": t.onboarding_level_title,
    "onboarding-level-el": t.onboarding_level_prompt,
    "level-normal-label": t.level_normal,
    "level-simple-label": t.level_simple,
    "level-voice-label": t.level_voice,
    "saveProfileBtn": t.btn_save_start,
    "page-info-text": t.page_info_text,
    "resFooterBackBtn": t.btn_footer_back,
    "resFooterNextBtn": t.btn_footer_next,
    "resFooterReplayBtn": t.btn_footer_replay,
    "hero-tagline": t.hero_tagline,
    "hero-instructions": t.hero_instructions,
    "play-btn-text": t.btn_play,
    "processingStatus": t.progress_1,
    "processing-subtext-el": t.processing_subtext
  };

  for (const [id, val] of Object.entries(locMap)) {
    const el = document.getElementById(id);
    if (!el) continue;
    
    if (el.tagName === "INPUT" || el.tagName === "TEXTAREA") {
      el.placeholder = val;
    } else {
      // Use innerHTML for labels/onboarding to preserve icons (globe, brain, etc)
      if (id.includes("onboarding") || id.includes("level-") || id.includes("label") || id.includes("hero")) {
         el.innerHTML = val;
      } else {
         el.textContent = val;
      }
    }
  }
}

// --- Configuration ---
const STORAGE_KEY = "nagrik_history";
const CONFIG_KEY = "nagrik_config"; // New key for Nuclear Reset
const PROCESSING_TIMEOUT_MS = 180000;
const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;
const MAX_UPLOAD_RETRIES = 3;

function getProgressMessages() {
  const t = I18N[localStorage.getItem("nagrik_lang") || "hi"] || I18N.hi;
  return [t.progress_1, t.progress_2, t.progress_3, t.progress_4, t.progress_5, t.progress_6];
}

// --- Memory Hardening Utility (Phase 7) ---
const MemoryManager = {
  purgeAudio() {
    console.log(`MemoryManager: Purging ${fieldAudioCache.size} audio objects...`);
    fieldAudioCache.forEach((audio, key) => {
      audio.pause();
      audio.src = "";
      audio.load(); // Forces resources to be freed
    });
    fieldAudioCache.clear();
    
    // Also clear main page audio
    if (audioPlayer) {
      audioPlayer.pause();
      audioPlayer.src = "";
    }
  },
  
  revoke(url) {
    if (url && url.startsWith('blob:')) {
      URL.revokeObjectURL(url);
    }
  },

  cleanupSession() {
    this.purgeAudio();
    // Clear DOM container to help GC
    if (pagesContainer) pagesContainer.innerHTML = "";
  }
};

// --- Local Storage Wrapper ---
const Storage = {
  save(doc) {
    let items = this.getAll();
    items.unshift(doc);
    if (items.length > 10) items.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
    this.hydrateLists();
  },
  getAll() {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  },
  hydrateLists() {
    const items = this.getAll();
    [recentActivityList, historyList].forEach(list => {
      if (!list) return;
      if (items.length === 0) {
        // preserve empty state if needed
        return;
      }
      list.innerHTML = "";
      items.forEach(item => {
        const div = document.createElement("div");
        div.className = "activity-item";
        div.innerHTML = `
          <div class="activity-icon">📄</div>
          <div class="activity-info" style="flex:1">
            <h4>${item.filename}</h4>
            <p>${new Date(item.timestamp).toLocaleDateString()}</p>
          </div>
          <div style="display:flex; gap: 8px;">
            <button class="view-doc-btn" data-id="${item.id}">View</button>
            <button class="delete-doc-btn" data-id="${item.id}" style="background:rgba(255,0,0,0.1); color:red; border:none; padding:8px; border-radius:8px;">🗑️</button>
          </div>
        `;
        div.querySelector('.view-doc-btn').onclick = () => {
             resultsSection.dataset.currentId = item.id;
             renderResult(item);
             switchView("scan");
        };
        div.querySelector('.delete-doc-btn').onclick = async (e) => {
            e.stopPropagation();
            if (confirm("Delete document from record?")) {
                await deleteHistoryItem(item.job_id, item.id);
            }
        };
        list.appendChild(div);
      });
    });
  }
};

async function deleteHistoryItem(jobId, storageId) {
  try {
      await fetch(`/api/history/${jobId}`, { 
          method: "DELETE",
          headers: getAuthHeader()
      });
      let items = Storage.getAll();
      items = items.filter(it => it.id !== storageId);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
      Storage.hydrateLists();
  } catch (err) {
      console.error("Delete failed", err);
  }
}

// --- Image Optimization (Hardening 5: Atomic Purge) ---
async function compressImage(file, maxWidth = 1600, maxHeight = 1600, quality = 0.8) {
  if (!file.type.startsWith('image/')) return file;
  
  return new Promise((resolve, reject) => {
    const objectUrl = URL.createObjectURL(file);
    const img = new Image();
    
    img.onload = () => {
      const canvas = document.createElement('canvas');
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxWidth) {
          height *= maxWidth / width;
          width = maxWidth;
        }
      } else {
        if (height > maxHeight) {
          width *= maxHeight / height;
          height = maxHeight;
        }
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(img, 0, 0, width, height);

      // Clean up source URL immediately
      MemoryManager.revoke(objectUrl);

      canvas.toBlob((blob) => {
        if (!blob) {
          canvas.width = 0; canvas.height = 0; img.src = "";
          resolve(file); return;
        }
        
        const compressedFile = new File([blob], file.name, {
          type: 'image/jpeg',
          lastModified: Date.now()
        });

        // Final Atomic Purge (Hardening 5)
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        canvas.width = 0;
        canvas.height = 0;
        
        // Kill the Image object bitmap
        img.src = "";
        
        console.log(`Atomic Compression: ${(file.size / 1024 / 1024).toFixed(2)}MB -> ${(compressedFile.size / 1024 / 1024).toFixed(2)}MB`);
        resolve(compressedFile);
      }, 'image/jpeg', quality);
    };

    img.onerror = () => {
      img.src = ""; 
      MemoryManager.revoke(objectUrl);
      resolve(file);
    };
    
    img.src = objectUrl;
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getUploadReadyFile(rawFile, statusEl) {
  if (!rawFile.type.startsWith('image/')) {
    if (rawFile.size > MAX_UPLOAD_BYTES) {
      throw new Error("File is too large. Please upload a file up to 10 MB.");
    }
    return rawFile;
  }

  let current = await compressImage(rawFile, 1600, 1600, 0.8);
  let quality = 0.7;
  let dimension = 1400;
  let attempts = 0;

  while (current.size > MAX_UPLOAD_BYTES && attempts < 4) {
    attempts += 1;
    statusEl.textContent = `Optimizing photo for upload (${attempts}/4)...`;
    current = await compressImage(current, dimension, dimension, quality);
    quality = Math.max(0.45, quality - 0.1);
    dimension = Math.max(900, Math.floor(dimension * 0.85));
  }

  if (current.size > MAX_UPLOAD_BYTES) {
    throw new Error("Photo is still too large after compression. Please crop or retake and keep it under 10 MB.");
  }

  return current;
}

async function fetchWithRetry(url, options, maxAttempts = MAX_UPLOAD_RETRIES) {
  let lastError = null;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    try {
      return await fetch(url, options);
    } catch (error) {
      lastError = error;
      if (attempt === maxAttempts) {
        break;
      }
      const waitMs = Math.min(1000 * (2 ** (attempt - 1)), 4000);
      await sleep(waitMs);
    }
  }
  throw lastError || new Error("Network error");
}

function getPollDelayMs(attempt) {
  if (attempt < 15) return 1200;
  if (attempt < 40) return 1800;
  if (attempt < 80) return 2500;
  return 3500;
}

// --- View Navigation ---
function switchView(target) {
  Object.values(views).forEach(v => { if(v) v.hidden = true; });
  Object.values(navItems).forEach(n => { if(n) n.classList.remove("active"); });

  if (views[target]) {
    views[target].hidden = false;
    if(navItems[target]) navItems[target].classList.add("active");
  }

  // Hide bottom nav if login is active
  const bottomNav = document.querySelector(".bottom-nav");
  if (bottomNav) {
    bottomNav.style.display = (target === "login") ? "none" : "flex";
  }

  // Toggle AskAI button visibility
  if (askAIToggleBtn) {
    askAIToggleBtn.style.display = (target === "login") ? "none" : "flex";
  }

  if (target === "scan") {
    if (resultsSection.hidden) {
      gotoScanStep(1);
      document.body.classList.remove("results-active");
    } else {
      document.body.classList.add("results-active");
    }
  } else {
    document.body.classList.remove("results-active");
  }
}

function gotoScanStep(step) {
  Object.values(scanSteps).forEach(s => { if(s) s.hidden = true; });
  Object.values(scanLabels).forEach(l => { if(l) l.classList.remove("active"); });

  if (scanSteps[step]) scanSteps[step].hidden = false;
  if (scanLabels[step]) scanLabels[step].classList.add("active");
}

// --- Sensory Helpers (Hardening 2) ---
function playSuccessSound() {
  // 1. Try Local User Audio (Mounted under /static)
  const localAudio = new Audio("/static/assets/success.mp3");
  
  localAudio.play().then(() => {
    console.log("Playing user-provided success sound.");
  }).catch(() => {
    // 2. Fallback to Premium Web Audio
    const webAudio = new Audio("https://www.soundjay.com/buttons/sounds/button-09.mp3");
    webAudio.play().catch(err => {
      console.warn("Local and Web audio failed, using fallback synth:", err);
      // 3. Final Fallback: Premium Synth (Dual Chime)
      try {
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (!AudioContext) return;
        const context = new AudioContext();
        const playChime = (freq, start, duration) => {
          const osc = context.createOscillator();
          const gain = context.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, start);
          gain.gain.setValueAtTime(0, start);
          gain.gain.linearRampToValueAtTime(0.1, start + 0.02);
          gain.gain.exponentialRampToValueAtTime(0.01, start + duration);
          osc.connect(gain);
          gain.connect(context.destination);
          osc.start(start);
          osc.stop(start + duration);
        };
        playChime(880, context.currentTime, 0.4); 
        playChime(1108.73, context.currentTime + 0.1, 0.5);
      } catch (e) { console.error("Total audio failure:", e); }
    });
  });
}
// --- Compression Simulation (Phase 8) ---
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

async function simulateCompression(file) {
    const compressionStats = document.getElementById("compressionStats");
    const originalSizeEl = document.getElementById("originalSize");
    const compressedSizeEl = document.getElementById("compressedSize");
    const savedPercentEl = document.getElementById("savedPercent");
    const progressBar = document.getElementById("compressionProgressBar");
    const statusMsg = document.getElementById("processingStatus");

    if (!compressionStats || !progressBar) return;

    // Show simulation UI
    compressionStats.style.display = "block";
    
    const originalSizeBytes = file.size;
    const isImage = file.type.startsWith('image/');
    const ratio = isImage ? 0.15 : 0.85; // 85% reduction for images, 15% for PDFs (Visual simulation)
    const targetSizeBytes = Math.round(originalSizeBytes * ratio);
    const targetSavedPercent = Math.round((1 - ratio) * 100);

    originalSizeEl.textContent = formatBytes(originalSizeBytes);

    const duration = 1800; // 1.8 seconds for premium feel
    const start = performance.now();

    return new Promise(resolve => {
        function update(now) {
            const elapsed = now - start;
            const progress = Math.min(elapsed / duration, 1);
            
            // Vishwa Progress Bar Update
            progressBar.style.width = `${progress * 100}%`;
            
            // Stats Count-up
            const currentCompressed = Math.round(originalSizeBytes - (originalSizeBytes - targetSizeBytes) * progress);
            const currentSaved = Math.round(targetSavedPercent * progress);
            
            compressedSizeEl.textContent = formatBytes(currentCompressed);
            savedPercentEl.textContent = `${currentSaved}%`;

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                setTimeout(() => {
                    compressionStats.style.display = "none";
                    resolve();
                }, 400);
            }
        }
        requestAnimationFrame(update);
    });
}






// --- Auth Logic ---
function generateCaptcha() {
  const chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"; // Removed ambiguous chars like 0, O, 1, I
  let result = "";
  for (let i = 0; i < 5; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  currentCaptcha = result;
  if (captchaCodeDisplay) {
    captchaCodeDisplay.textContent = result;
  }
}

// --- Auth Logic (Phase 10: JWT & Session-Ephemeral) ---
function getAuthHeader() {
  const token = localStorage.getItem("nagrik_jwt");
  return token ? { "Authorization": `Bearer ${token}` } : {};
}

function toggleAuthMode() {
  isRegisterMode = !isRegisterMode;
  loginErrorEl.hidden = true;
  loginSuccessEl.hidden = true;
  
  if (isRegisterMode) {
    document.querySelector(".login-header h2").textContent = "Nagrik Register";
    fullNameGroup.hidden = false;
    loginBtnText.textContent = "Create Account / खाता बनाएं";
    toggleMsg.textContent = "Already have an account? / क्या आपका खाता पहले से है?";
    toggleAuthBtn.textContent = "Login / लॉगिन करें";
  } else {
    document.querySelector(".login-header h2").textContent = "Nagrik Login";
    fullNameGroup.hidden = true;
    loginBtnText.textContent = "Login / लॉगिन करें";
    toggleMsg.textContent = "Don't have an account? / क्या आपका खाता नहीं है?";
    toggleAuthBtn.textContent = "Create Account / खाता बनाएं";
  }
  generateCaptcha();
  captchaInput.value = "";
}

async function validateAuth() {
  if (isRegisterMode) {
    await handleRegister();
  } else {
    await validateLogin();
  }
}

async function handleRegister() {
  const name = registerNameInput.value.trim();
  const mobile = loginMobileInput.value.trim();
  const pass = loginPassInput.value.trim();
  const enteredCaptcha = captchaInput.value.trim().toUpperCase();

  loginErrorEl.hidden = true;
  loginSuccessEl.hidden = true;

  if (!name) {
    showLoginError("Please enter your full name.");
    return;
  }
  if (!mobile || mobile.length < 10) {
    showLoginError("Please enter a valid 10-digit mobile number.");
    return;
  }
  if (!pass || pass.length < 6) {
    showLoginError("Password must be at least 6 characters.");
    return;
  }
  if (enteredCaptcha !== currentCaptcha) {
    showLoginError("Invalid CAPTCHA.");
    generateCaptcha();
    return;
  }

  loginBtn.disabled = true;
  loginBtnText.hidden = true;
  loginSpinner.hidden = false;

  try {
    const formData = new FormData();
    formData.append("full_name", name);
    formData.append("mobile", mobile);
    formData.append("password", pass);

    const res = await fetch("/api/auth/register", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (!res.ok) {
        throw new Error(data.detail || "Registration failed.");
    }

    loginSuccessEl.textContent = data.message;
    loginSuccessEl.hidden = false;
    
    // Switch to login mode after 2s
    setTimeout(() => {
      toggleAuthMode();
      loginSuccessEl.hidden = true;
    }, 2000);

  } catch (err) {
    showLoginError(err.message);
  } finally {
    loginBtn.disabled = false;
    loginBtnText.hidden = false;
    loginSpinner.hidden = true;
  }
}

async function validateLogin() {
  const mobile = loginMobileInput.value.trim();
  const pass = loginPassInput.value.trim();
  const enteredCaptcha = captchaInput.value.trim().toUpperCase();

  loginErrorEl.hidden = true;

  if (!mobile || mobile.length < 10) {
    showLoginError("Please enter a valid 10-digit mobile number.");
    return;
  }
  if (!pass) {
    showLoginError("Please enter your password.");
    return;
  }
  if (enteredCaptcha !== currentCaptcha) {
    showLoginError("Invalid CAPTCHA. Please try again.");
    generateCaptcha();
    captchaInput.value = "";
    document.querySelector(".login-card").classList.add("shake");
    setTimeout(() => document.querySelector(".login-card").classList.remove("shake"), 400);
    return;
  }

  // Success flow
  loginBtn.disabled = true;
  loginBtnText.hidden = true;
  loginSpinner.hidden = false;

  try {
    const formData = new FormData();
    formData.append("mobile", mobile);
    formData.append("password", pass);

    const res = await fetch("/api/token", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error("Invalid mobile or password.");
    }

    const { access_token } = await res.json();
    localStorage.setItem("nagrik_jwt", access_token);
    localStorage.setItem(LOG_AUTH_KEY, "true");
    
    switchView("home");
    initApp(); // Refresh state

    // Haptic feedback
    if (navigator.vibrate) navigator.vibrate(50);
  } catch (err) {
    showLoginError(err.message);
    generateCaptcha();
  } finally {
    loginBtn.disabled = false;
    loginBtnText.hidden = false;
    loginSpinner.hidden = true;
  }
}

async function handleLogout() {
  try {
    const headers = getAuthHeader();
    await fetch("/api/auth/logout", { method: "POST", headers });
  } catch (e) {
    console.warn("Logout cleanup failed", e);
  } finally {
    localStorage.removeItem(LOG_AUTH_KEY);
    localStorage.removeItem("nagrik_jwt");
    localStorage.removeItem(STORAGE_KEY); // Purge local history
    window.location.reload();
  }
}

// Session-Ephemeral: Cleanup on tab close/leave
window.addEventListener("beforeunload", (event) => {
  if (localStorage.getItem(LOG_AUTH_KEY) === "true") {
    const token = localStorage.getItem("nagrik_jwt");
    if (token) {
      // Use deliverBeacon for reliable cleanup on close
      const url = "/api/auth/logout";
      // Fetch with keepalive is better than beacon for JSON/Headers
      fetch(url, { 
        method: "POST", 
        headers: { "Authorization": `Bearer ${token}` },
        keepalive: true 
      });
    }
  }
});

function showLoginError(msg) {
  loginErrorEl.textContent = msg;
  loginErrorEl.hidden = false;
}

// --- Event Listeners ---
startScanBtn.onclick = () => switchView("scan");
if (newScanShortBtn) newScanShortBtn.onclick = () => switchView("scan");
takePhotoBtn.onclick = () => cameraInput.click();
uploadFileBtn.onclick = () => fileInput.click();
cancelStepBtn.onclick = () => gotoScanStep(1);

Object.entries(navItems).forEach(([key, el]) => {
  if(el) el.onclick = (e) => {
    e.preventDefault();
    switchView(key);
  };
});

// File Handlers
[cameraInput, fileInput].forEach(input => {
  input.onchange = (e) => {
    const file = e.target.files[0];
    if (file) {
      confirmFileName.textContent = file.name;
      gotoScanStep(2);
    }
  };
});

processBtn.onclick = async () => {
  const rawFile = cameraInput.files[0] || fileInput.files[0];
  if (!rawFile) return;

  // RAM Surgery Start: Purge previous session data
  MemoryManager.cleanupSession();

  gotoScanStep(3);
  const statusMsg = document.getElementById("processingStatus");
  statusMsg.textContent = "Hardening memory for mobile...";
  
  // Sequential Simulation (Phase 8)
  await simulateCompression(rawFile);
  
  statusMsg.textContent = "Starting analysis...";
  
  let file = null;
  let msgInterval = null;
  const uploadController = new AbortController();
  const hardTimeout = setTimeout(() => uploadController.abort(), PROCESSING_TIMEOUT_MS);
  processBtn.disabled = true;
  
  const messages = getProgressMessages();
  let msgIdx = 0;

  try {
    file = await getUploadReadyFile(rawFile, statusMsg);

    // ATOMIC PURGE: Clear the heavy input handle from RAM
    cameraInput.value = "";
    fileInput.value = "";

    msgInterval = setInterval(() => {
      statusMsg.textContent = messages[msgIdx % messages.length];
      msgIdx++;
    }, 1500);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("language", localStorage.getItem("nagrik_lang") === "hi" ? "Hindi" : "English");
    formData.append("level", localStorage.getItem("nagrik_level") || 2);
    formData.append("lightweight", lightweightToggle.checked);

    const res = await fetchWithRetry("/api/process", {
      method: "POST",
      headers: getAuthHeader(),
      body: formData,
      signal: uploadController.signal,
    });

    if (!res.ok) {
      if (res.status === 413) {
        throw new Error("File is too large. Please upload a file up to 10 MB.");
      }
      if (res.status >= 500) {
        throw new Error("Server is busy right now. Please retry in a moment.");
      }
      throw new Error("Upload failed. Please check the selected file and connection.");
    }

    const { job_id } = await res.json();
    
    // Polling Logic
    let jobDone = false;
    let pollAttempts = 0;
    const pollStarted = Date.now();
    
    while (!jobDone && (Date.now() - pollStarted) < PROCESSING_TIMEOUT_MS) {
      pollAttempts++;
      await sleep(getPollDelayMs(pollAttempts));
      
      const pollRes = await fetch(`/api/status/${job_id}`, { 
          signal: uploadController.signal,
          headers: getAuthHeader()
      });
      if (!pollRes.ok) continue;
      
      const job = await pollRes.json();
      if (job.status === "completed") {
        jobDone = true;
        
        // --- Sensory Package (Hardening 2) ---
        if (navigator.vibrate) navigator.vibrate([100, 50, 100]);
        playSuccessSound();
        resultsSection.classList.add("success-pulse");
        document.body.classList.add("completion-glow");
        setTimeout(() => {
          resultsSection.classList.remove("success-pulse");
          document.body.classList.remove("completion-glow");
        }, 2000);

        const docRecord = {
          id: uuidv4(),
          job_id: job_id, // Store job_id for AI Chatbot structural context
          timestamp: Date.now(),
          ...job.result
        };
        Storage.save(docRecord);
        renderResult(docRecord);
      }

      else if (job.status === "failed") {
        throw new Error(job.error || "Analysis failed");
      }
      // Continue polling if "pending" or "processing"
    }
    
    if (!jobDone) throw new Error("Processing took too long on this network. Please retry with clearer or smaller photo.");

  } catch (err) {
    if (err.name === "AbortError") {
      processingStatus.textContent = "Request timed out. Please try again on a stronger network.";
    } else {
      processingStatus.textContent = err.message || "Error: Please check your connection and try again.";
    }
    console.error("Analysis Error:", err.message || err);
  } finally {
    clearTimeout(hardTimeout);
    processBtn.disabled = false;
    if (msgInterval) clearInterval(msgInterval);
  }
};

// --- Render Logic ---
function renderResult(data) {
  resultsSection.hidden = false;
  resultsSection.dataset.currentId = data.id;
  document.body.classList.add("results-active");
  
  // Hide scan steps
  Object.values(scanSteps).forEach(s => { if(s) s.hidden = true; });

  // Update Hero/Summary
  const tagline = document.getElementById("hero-tagline");
  if (tagline) {
    tagline.textContent = data.overall_summary || data.document_purpose || "Document processed successfully.";
  }
  
  // Audio Player Setup
  if (data.audio_url) {
    audioController.style.display = "block";
    audioPlayer.src = data.audio_url;
  } else {
    audioController.style.display = "none";
  }

  // Render Page Tabs
  const pageTabs = document.getElementById("pageTabs");
  pageTabs.innerHTML = "";
  data.pages.forEach((p, idx) => {
    const btn = document.createElement("button");
    btn.className = idx === 0 ? "tab-btn pill-tab active" : "tab-btn pill-tab";
    btn.textContent = `पेज ${idx + 1}`;
    btn.onclick = () => {
      document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderFields(p.fields, p.page, p);
      pageTabs.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    pageTabs.appendChild(btn);
  });

  // Initial render of first page
  if (data.pages && data.pages.length > 0) {
    renderFields(data.pages[0].fields, data.pages[0].page, data.pages[0]);
  }
}

// --- Help Functions ---
function getFieldIcon(name) {
  const n = name.toLowerCase();
  if (n.includes("नाम") || n.includes("name") || n.includes("user")) return "👤";
  if (n.includes("पिता") || n.includes("पति") || n.includes("father") || n.includes("husband")) return "📇";
  if (n.includes("आधार") || n.includes("aadhaar") || n.includes("id") || n.includes("number")) return "🆔";
  if (n.includes("मोबाइल") || n.includes("phone") || n.includes("mobile")) return "📱";
  if (n.includes("बैंक") || n.includes("bank") || n.includes("ifsc") || n.includes("खाता")) return "🏦";
  if (n.includes("पता") || n.includes("address") || n.includes("गांव")) return "🏠";
  if (n.includes("तारीख") || n.includes("date") || n.includes("जन्म")) return "📅";
  if (n.includes("लिंग") || n.includes("gender")) return "🚻";
  return "📄"; // Default
}

function renderFields(fields, pageNum, pageData = null) {
  pagesContainer.innerHTML = "";
  if (!fields || fields.length === 0) {
    const lang = localStorage.getItem("nagrik_lang") || "hi";
    const pageType = ((pageData && pageData.page_type) || "").toLowerCase();
    const infoLikePage = pageType.includes("instruction") || pageType.includes("declaration") || pageType.includes("signature");
    const message = infoLikePage
      ? (lang === "hi"
          ? "इस पेज पर भरने वाला कोई फील्ड नहीं है। यह जानकारी वाला पेज लगता है।"
          : "No fillable fields on this page. It looks like an informational page.")
      : (lang === "hi"
          ? "इस पेज के फील्ड साफ नहीं पढ़े गए। कृपया साफ रोशनी में फोटो लेकर दोबारा स्कैन करें।"
          : "Fields could not be read clearly on this page. Please retake a clearer photo and scan again.");
    pagesContainer.innerHTML = `<div class="empty-state">${message}</div>`;
    return;
  }

  fields.forEach((f, idx) => {
    const row = document.createElement("div");
    row.className = "field-row-nagrik fade-up";
    row.style.animationDelay = `${idx * 0.1}s`;
    
    const lang = localStorage.getItem("nagrik_lang") || "hi";
    const t = I18N[lang] || I18N.hi;

    const fieldName = f.field_name || f.label || "जानकारी";
    const whatToFill = f.what_to_fill || f.simplified || "---";
    const whyItMatters = f.why_it_matters || f.context || "---";
    const exampleVal = f.example || "---";
    const isRequired = true; // In rural forms, most are required

    row.innerHTML = `
      <div class="field-col-numbers">
        <div class="step-circle">${idx + 1}</div>
        <div class="field-icon-circle">${getFieldIcon(fieldName)}</div>
      </div>
      
      <div class="field-col-data">
        <div class="field-title-row">
          <h3>${fieldName}</h3>
          ${isRequired ? `<span class="tag-required">${t.important || "जरूरी"}</span>` : ""}
        </div>
        <div class="field-instruction-line">
          <strong>क्या भरना है:</strong> ${whatToFill}
        </div>
        <div class="field-instruction-line" style="font-size: 14px; color: #4a5568;">
          <strong>क्यों:</strong> ${whyItMatters}
        </div>
      </div>
      
      <div class="field-col-action">
        <div class="example-box-nagrik">
          <span class="label">उदाहरण</span>
          <p class="val">${exampleVal}</p>
        </div>
        <button class="btn-audio-mini" data-text="${whatToFill}. ${whyItMatters}. ${exampleVal}">
          <span class="icon">🔊</span> सुनें
        </button>
      </div>
    `;
    
    // Custom logic for Adhaar warning bar (1:1 match attempt)
    if (fieldName.includes("आधार") || fieldName.includes("Aadhaar")) {
      const warningBar = document.createElement("div");
      warningBar.className = "note-bar";
      warningBar.innerHTML = `<span>⚠️</span> <strong>ध्यान दें:</strong> आधार नंबर 12 अंकों का ही होना चाहिए। स्पेस या डैश न लगाएं।`;
      row.after(warningBar);
    }
    
    const listenBtn = row.querySelector(".btn-audio-mini");
    listenBtn.onclick = async () => {
      const text = listenBtn.dataset.text;
      const originalHtml = listenBtn.innerHTML;
      listenBtn.innerHTML = `<span>⏳</span> ...`;
      listenBtn.classList.add("loading");
      
      try {
        const res = await fetch("/api/tts-field", {
          method: "POST",
          headers: { 
              "Content-Type": "application/x-www-form-urlencoded",
              ...getAuthHeader()
          },
          body: new URLSearchParams({ text, lang: lang })
        });
        const audioData = await res.json();
        
        // Hardening 4: Manage audio lifecycle
        const fieldAudio = new Audio(audioData.audio_url);
        
        // Clear previous audio for this field if it exists
        if (fieldAudioCache.has(text)) {
           const old = fieldAudioCache.get(text);
           old.pause();
           old.src = "";
        }
        
        fieldAudioCache.set(text, fieldAudio);
        fieldAudio.play();
      } catch (e) {
        console.error(e);
      } finally {
        listenBtn.innerHTML = originalHtml;
        listenBtn.classList.remove("loading");
      }
    };
    
    pagesContainer.appendChild(row);
  });
}

// --- Audio Controller Logic ---
playPauseBtn.onclick = () => {
  if (audioPlayer.paused) {
    audioPlayer.play();
    playPauseBtn.innerHTML = I18N[localStorage.getItem("nagrik_lang") || "hi"].btn_pause;
  } else {
    audioPlayer.pause();
    playPauseBtn.innerHTML = I18N[localStorage.getItem("nagrik_lang") || "hi"].btn_play;
  }
};

audioPlayer.ontimeupdate = () => {
  const percent = (audioPlayer.currentTime / audioPlayer.duration) * 100;
  audioProgress.value = percent || 0;
  currentTimeEl.textContent = formatTime(audioPlayer.currentTime);
};

audioPlayer.onloadedmetadata = () => {
  durationTimeEl.textContent = formatTime(audioPlayer.duration);
  const display = document.getElementById("durationTimeDisplay");
  if(display) display.textContent = formatTime(audioPlayer.duration);
};

function formatTime(secs) {
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s < 10 ? '0' : ''}${s}`;
}

// --- Ask AI Logic ---
const askAIPanel = document.getElementById("askAIPanel");
const askAiCtaBtn = document.getElementById("askAiCtaBtn");
const askAIInput = document.getElementById("askAIInput");
const askAISendBtn = document.getElementById("askAISendBtn");

if (askAiCtaBtn) {
    askAiCtaBtn.onclick = () => {
        askAIPanel.hidden = false;
        askAIPanel.style.display = "flex";
    };
}

askAIToggleBtn.onclick = () => {
    askAIPanel.hidden = !askAIPanel.hidden;
    if(!askAIPanel.hidden) askAIPanel.style.display = "flex";
    else askAIPanel.style.display = "none";
};

closeAskAIBtn.onclick = () => {
    askAIPanel.hidden = true;
    askAIPanel.style.display = "none";
};

askAISendBtn.onclick = () => {
    const q = askAIInput.value.trim();
    if (q) {
        handleAIQuestion(q);
        askAIInput.value = "";
    }
};

askAIInput.onkeypress = (e) => {
    if (e.key === "Enter") {
        askAISendBtn.click();
    }
};

// Real Speech Recognition initialization
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;
if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
}

function addChatMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `chat-message ${role}`;
    msgDiv.textContent = text;
    askAIChat.appendChild(msgDiv);
    askAIChat.scrollTop = askAIChat.scrollHeight;
}

async function handleAIQuestion(question) {
    const lang = localStorage.getItem("nagrik_lang") || "hi";
    const t = I18N[lang] || I18N.hi;
    
    addChatMessage("user", question);
    
    // Get context from currently selected document and page
    let contextMd = "";
    let contextSummary = "";
    let contextGuidelines = "";
    let fieldContext = "";
    const activeBtn = document.querySelector(".tab-btn.active");
    const currentDocId = resultsSection.dataset.currentId;
    
    if (activeBtn && currentDocId) {
        const pageText = activeBtn.textContent.trim();
        const pageNumMatch = pageText.match(/\d+/);
        // Correct off-by-one: UI is 1-indexed, data is 0-indexed
        const pageNum = pageNumMatch ? parseInt(pageNumMatch[0]) - 1 : 0;
        
        const history = Storage.getAll();
        const currentDoc = history.find(d => d.id === currentDocId);
        
        if (currentDoc && currentDoc.pages) {
            const pageData = currentDoc.pages.find(p => p.page === pageNum);
            if (pageData) {
                contextMd = pageData.original_markdown || ""; 
                contextSummary = (currentDoc.document_purpose ? currentDoc.document_purpose + "\n" : "") + (pageData.page_summary || "");
                
                // Format guidelines
                if (pageData.retrieved_guidelines && pageData.retrieved_guidelines.length > 0) {
                    contextGuidelines = "- " + pageData.retrieved_guidelines.join("\n- ");
                }

                // Format simplified field guide (Critical fix for "I don't know" errors)
                if (pageData.fields && pageData.fields.length > 0) {
                    fieldContext = pageData.fields.map(f => 
                        `- [${f.field_name || "Field"}]: ${f.what_to_fill || "No instruction"} (Reason: ${f.why_it_matters || "Required"})`
                    ).join("\n");
                }
            }
        }
    }

    micLabel.textContent = t.ask_ai_thinking;
    
    try {
        const formData = new FormData();
        formData.append("question", question);
        formData.append("page_context", contextMd);
        formData.append("page_summary", contextSummary);
        formData.append("guideline_context", contextGuidelines);
        formData.append("field_context", fieldContext);
        formData.append("language", lang === "hi" ? "Hindi" : "English");
        
        // Pass job_id and session_id for cross-page memory
        const currentDoc = Storage.getAll().find(d => d.id === currentDocId);
        if (currentDoc && currentDoc.job_id) {
            formData.append("job_id", currentDoc.job_id);
        }
        
        // Use a simple device-fixed session ID for now, or per-document session
        formData.append("session_id", "session_" + (currentDocId || "global").substring(0, 8));


        const res = await fetch("/api/ask", { 
            method: "POST", 
            body: formData,
            headers: getAuthHeader() 
        });
        const data = await res.json();
        
        if (data.answer) {
            addChatMessage("sys", data.answer);
            speakResponse(data.answer, lang);
        } else {
            addChatMessage("sys", t.ask_ai_error || "Error generating answer.");
        }
    } catch (err) {
        console.error("Ask AI Error:", err);
        addChatMessage("sys", t.ask_ai_error || "Network error.");
    } finally {
        micLabel.textContent = t.ask_ai_btn || "Ask AI";
    }
}

async function speakResponse(text, lang) {
    try {
        const res = await fetch("/api/tts-field", {
            method: "POST",
            headers: { 
                "Content-Type": "application/x-www-form-urlencoded",
                ...getAuthHeader()
            },
            body: new URLSearchParams({ text, lang: lang })
        });
        const audioData = await res.json();
        if (audioData.audio_url) {
            // Hardening 4: Ensure single instance or cleanup
            if (voiceResponseAudio.src) {
                voiceResponseAudio.pause();
                voiceResponseAudio.src = "";
            }
            voiceResponseAudio.src = audioData.audio_url;
            voiceResponseAudio.play();
        }
    } catch (e) {
        console.error("TTS failed", e);
    }
}

let isListening = false;
voiceMicBtn.onclick = () => {
    if (!recognition) {
        alert("Speech recognition not supported in this browser.");
        return;
    }

    if (isListening) {
        recognition.stop();
        return;
    }

    const lang = localStorage.getItem("nagrik_lang") || "hi";
    const t = I18N[lang] || I18N.hi;
    
    try {
        isListening = true;
        voiceMicBtn.classList.add("listening");
        micLabel.textContent = t.ask_ai_listening || "Listening...";
        voiceTranscript.hidden = false;
        voiceTranscript.textContent = "...";
        
        recognition.lang = lang === "hi" ? "hi-IN" : "en-US";
        recognition.start();

        recognition.onresult = (event) => {
            isListening = false;
            voiceMicBtn.classList.remove("listening");
            const transcript = event.results[0][0].transcript;
            voiceTranscript.textContent = transcript;
            handleAIQuestion(transcript);
        };

        recognition.onspeechend = () => {
            recognition.stop();
        };

        recognition.onerror = (event) => {
            isListening = false;
            voiceMicBtn.classList.remove("listening");
            console.error("Speech Recognition Error:", event.error);
            micLabel.textContent = t.ask_ai_error || "Error";
            if (event.error === 'no-speech') {
                addChatMessage("sys", lang === "hi" ? "आवाज़ नहीं सुनाई दी।" : "No speech detected.");
            }
        };

        recognition.onend = () => {
            isListening = false;
            voiceMicBtn.classList.remove("listening");
        };

    } catch (err) {
        console.error("Speech Start Error:", err);
        isListening = false;
        voiceMicBtn.classList.remove("listening");
    }
};

// --- Profile Onboarding (Nagrik Reset) ---
let selectedLang = "hi";
let selectedLevel = "2";

// Add default selection indicators
document.querySelector('.selection-card[data-lang="hi"]')?.classList.add('selected');
document.querySelector('.selection-card[data-level="2"]')?.classList.add('selected');

// Nuclear Logic: If new config not set, force onboarding
if (!localStorage.getItem(CONFIG_KEY)) {
    onboardingModal.hidden = false;
    onboardingModal.style.display = "flex";
    onboardingSection1.hidden = false;
    onboardingSection1.style.display = "block";
    onboardingSection2.hidden = true;
    onboardingSection2.style.display = "none";
    applyLanguage("hi"); // Default to Hindi
} else {
    applyLanguage(localStorage.getItem("nagrik_lang") || "hi");
}

document.querySelectorAll('.selection-card[data-lang]').forEach(card => {
    card.onclick = () => {
        document.querySelectorAll('.selection-card[data-lang]').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedLang = card.dataset.lang;
        applyLanguage(selectedLang);
        setTimeout(() => {
            onboardingSection1.hidden = true;
            onboardingSection1.style.display = "none";
            onboardingSection2.hidden = false;
            onboardingSection2.style.display = "block";
        }, 400);
    };
});

// --- Results Navigation Logic ---
resultsBackBtn.onclick = () => {
    resultsSection.hidden = true;
    document.body.classList.remove("results-active");
    switchView("scan");
    gotoScanStep(1);
};

resFooterBackBtn.onclick = () => {
    const activeBtn = document.querySelector(".tab-btn.active");
    if (activeBtn && activeBtn.previousElementSibling) {
        activeBtn.previousElementSibling.click();
    }
};

resFooterNextBtn.onclick = () => {
    const activeBtn = document.querySelector(".tab-btn.active");
    if (activeBtn && activeBtn.nextElementSibling) {
        activeBtn.nextElementSibling.click();
    }
};

resFooterReplayBtn.onclick = () => {
    if (audioPlayer.src) {
        audioPlayer.currentTime = 0;
        audioPlayer.play();
        playPauseBtn.innerHTML = I18N[localStorage.getItem("nagrik_lang") || "hi"].btn_pause;
    }
};

document.querySelectorAll('.selection-card[data-level]').forEach(card => {
    card.onclick = () => {
        document.querySelectorAll('.selection-card[data-level]').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        selectedLevel = card.dataset.level;
    };
});

saveProfileBtn.onclick = () => {
    localStorage.setItem("nagrik_lang", selectedLang);
    localStorage.setItem("nagrik_level", selectedLevel);
    localStorage.setItem(CONFIG_KEY, "set"); // Mark Nuclear Reset as complete
    
    saveProfileBtn.innerHTML = "✓ Saved";
    setTimeout(() => {
        onboardingModal.hidden = true;
        onboardingModal.style.display = "none";
        switchView("home");
    }, 400);
};

// --- UUID Polyfill ---
function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// --- Initialization ---
Storage.hydrateLists();

function initApp() {
  if (localStorage.getItem(LOG_AUTH_KEY) === "true") {
    // If logged in, check if onboarding is needed
    if (!localStorage.getItem(CONFIG_KEY)) {
        // Force onboarding if first time
        switchView("home"); // Dashboard background
        onboardingModal.hidden = false;
        onboardingModal.style.display = "flex";
        onboardingSection1.hidden = false;
        onboardingSection1.style.display = "block";
    } else {
        switchView("home");
    }
  } else {
    switchView("login");
    generateCaptcha();
  }
}

initApp();

// Event Listeners for Login
if (loginBtn) loginBtn.onclick = validateAuth;
if (toggleAuthBtn) toggleAuthBtn.onclick = toggleAuthMode;
if (logoutBtn) logoutBtn.onclick = handleLogout;
if (refreshCaptchaBtn) refreshCaptchaBtn.onclick = generateCaptcha;
// Allow enter key to login
if (loginMobileInput && loginPassInput && captchaInput) {
    [loginMobileInput, loginPassInput, captchaInput, registerNameInput].forEach(input => {
        if (!input) return;
        input.addEventListener("keypress", (e) => {
            if (e.key === "Enter") validateAuth();
        });
    });
}

// --- Phase 9: Cross-page Semantic Memory ---

// Navigation Listeners for Bottom Nav
Object.keys(navItems).forEach(key => {
  if (navItems[key]) {
      navItems[key].onclick = (e) => {
          e.preventDefault();
          switchView(key);
      };
  }
});

async function handleMemorySearch() {
  const query = memorySearchInput.value.trim();
  if (!query) return;

  const lang = localStorage.getItem("nagrik_lang") || "hi";
  const t = I18N[lang] || I18N.hi;

  // Show loading state
  memoryResults.innerHTML = `
    <div class="empty-state">
      <div class="spinner-mini" style="margin: 0 auto 16px auto; border-top-color: var(--color-primary);"></div>
      <p>${lang === "hi" ? "खोज रहे हैं..." : "Searching history..."}</p>
    </div>
  `;

  try {
      const formData = new FormData();
      formData.append("query", query);

      const res = await fetch("/api/memory/search", {
          method: "POST",
          body: formData,
          headers: getAuthHeader()
      });
      const data = await res.json();

      if (data.results && data.results.length > 0) {
          memoryResults.innerHTML = "";
          data.results.forEach(hit => {
              const div = document.createElement("div");
              div.className = "memory-item";
              div.innerHTML = `
                  <div class="meta">
                      <div class="filename">📄 ${hit.filename}</div>
                      <div class="page-badge">Page ${hit.page + 1}</div>
                  </div>
                  <div class="text">"${hit.text}"</div>
                  <div class="score-tag">
                      <span>🎯</span> ${lang === "hi" ? "सटीकता" : "Match"}: ${Math.round(hit.score * 100)}%
                  </div>
              `;
              div.onclick = () => {
                  const doc = Storage.getAll().find(d => d.id === hit.job_id);
                  if (doc) {
                      resultsSection.dataset.currentId = doc.id;
                      renderResult(doc);
                      switchView("scan");
                      // Scroll to specific page tab
                      setTimeout(() => {
                          const tab = document.querySelector(`.tab-btn[data-index="${hit.page}"]`);
                          if (tab) tab.click();
                      }, 100);
                  }
              };
              memoryResults.appendChild(div);
          });
      } else {
          memoryResults.innerHTML = `
            <div class="empty-state">
              <div class="icon">🏜️</div>
              <p>${t.mem_empty || "No matches found."}</p>
            </div>
          `;
      }
  } catch (err) {
      console.error("Memory search failed:", err);
      memoryResults.innerHTML = `<div class="empty-state"><p>Search unavailable.</p></div>`;
  }
}

if (memorySearchBtn) memorySearchBtn.onclick = handleMemorySearch;
if (memorySearchInput) {
  memorySearchInput.onkeypress = (e) => {
      if (e.key === "Enter") handleMemorySearch();
  };
}
