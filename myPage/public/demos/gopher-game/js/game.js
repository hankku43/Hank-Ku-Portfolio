let score = 0;
let gophercount = 0;
let currentDifficulty = 0;
let selectedDifficultyNumber = 1;
let currentDifficultyNumber = 1;
let currentLevel = 0;

const timer =document.querySelector(".timer");
const levelTimeSet = [10000,15000,20000];
const winScore = [10, 15, 20];
const playRegion = document.querySelector(".play_region");
const initialPage = document.querySelector(".game_initial_page");
const entry = document.querySelector(".entry");
const gameIntroduce = document.querySelector(".game_introduce");
const gameSetting = document.querySelector(".gamesetting");
const passPage = document.querySelector(".pass_page");
const fillPage = document.querySelector(".fill_page");
const winPage = document.querySelector(".win_page");
const allGameButton = document.querySelectorAll(".game_button");
const BGM =document.querySelector("#BGM");
const hoverSound = document.querySelector("#hover_sound");
const hitButtonSound = document.querySelector("#hitbutton_sound");
const countSound = document.querySelector("#count_sound");
const startSound = document.querySelector("#start_sound");
const gopherHert = document.querySelector("#gopher_hert");
startSound.volume = 0.25;
countSound.volume = 0.25;
const passSound = document.querySelector("#pass_sound");
const victorySound = document.querySelector("#victory_sound");
const fillSound = document.querySelector("#fill_sound");




const IsMobile = window.innerWidth <= 500;


// 音樂設定
let soundEffectVolume = 1;

function writingSoundEffect(soundEffectVolume){
    hoverSound.volume = soundEffectVolume;
    hitButtonSound.volume = soundEffectVolume;
    gopherHert.volume = soundEffectVolume;
    countSound.volume = soundEffectVolume/4;
    startSound.volume = soundEffectVolume/4;
    passSound.volume = soundEffectVolume;
    victorySound.volume = soundEffectVolume;
    fillSound.volume = soundEffectVolume;
}

function playBGM(){
    BGM.play();
    BGM.volume=0.5;
    console.log("BGM.volume: "+BGM.volume);
}
allGameButton.forEach(TheButton =>{
    TheButton.addEventListener("mouseenter",()=>{
        console.log("A game button is hover!");   
        // console.log(hoverSound);
        hoverSound.play();
    })
    TheButton.addEventListener("click",()=>{
        console.log("A game button is click!");
        // console.log(hitButtonSound);
        hitButtonSound.play();
    })
})
const bgmInput = document.querySelector('.bgmsetting_region input[type="range"]');
const soundEffectInput = document.querySelector('.soundeffectsetting_region input[type="range"]');
let currentBGM;
let currentEffect;
function muteBGM(){
    if(BGM.volume != 0){
        console.log("turn off sound");
        currentBGM = BGM.volume * 2;
        BGM.volume = 0;
        const volumeImg = document.querySelector(".bgmsetting_region img");
        volumeImg.src="img/thenosound.png";
        const input = bgmInput;
        input.value = 0;
        const volumeText = document.querySelector("#bgm_volume");
        volumeText.textContent = "0";
        console.log("BGM.volume: "+BGM.volume);
    }else{
        console.log("turn on sound");
        BGM.volume = currentBGM/2;
        const volumeImg = document.querySelector(".bgmsetting_region img");
        if(currentBGM > 0.5){
            volumeImg.src="img/thesound.png";
        }else{
            volumeImg.src="img/thehelfsound.png";
        }
        const input = bgmInput;
        input.value = currentBGM * 100;
        const volumeText = document.querySelector("#bgm_volume");
        volumeText.textContent = `${Math.round(currentBGM * 100)}`;
        console.log("BGM.volume: "+BGM.volume);
    }
}

function muteEffect(){
    if(soundEffectVolume != 0){
        console.log("turn off sound");
        currentEffect = soundEffectVolume;
        soundEffectVolume = 0;
        writingSoundEffect(soundEffectVolume);
        const volumeImg = document.querySelector(".soundeffectsetting_region img");
        volumeImg.src="img/thenosound.png";
        const input = soundEffectInput;
        input.value = 0;
        const volumeText = document.querySelector("#sound_volume");
        volumeText.textContent = "0";
        console.log("sound_volume: "+soundEffectVolume);
    }else{
        console.log("turn on sound");
        soundEffectVolume = currentEffect;
        writingSoundEffect(soundEffectVolume);
        const volumeImg = document.querySelector(".soundeffectsetting_region img");
        if(soundEffectVolume > 0.5){
            volumeImg.src="img/thesound.png";
        }else{
            volumeImg.src="img/thehelfsound.png";
        }
        const input = soundEffectInput;
        input.value = soundEffectVolume * 100;
        const volumeText = document.querySelector("#sound_volume");
        volumeText.textContent = `${Math.round(soundEffectVolume * 100)}`;
        console.log("sound_volume: "+soundEffectVolume);
    }
}

bgmInput.addEventListener('input', () => {
    const volume = bgmInput.value;
    const volumeText = document.querySelector("#bgm_volume");
    const volumeImg = document.querySelector(".bgmsetting_region img");
    BGM.volume = (volume / 100)/2;
    volumeText.textContent = volume;
    if(volume > 50){
        volumeImg.src = "img/thesound.png";
    } else if (volume <= 50 && volume != 0){
        volumeImg.src = "img/thehelfsound.png";
    } else {
        volumeImg.src = "img/thenosound.png";
        currentBGM = 0.5;
    }
    console.log("BGM.volume: "+BGM.volume);
});

soundEffectInput.addEventListener('input', () => {
    const volume = soundEffectInput.value;
    const volumeText = document.querySelector("#sound_volume");
    const volumeImg = document.querySelector(".soundeffectsetting_region img");
    soundEffectVolume = volume / 100;
    writingSoundEffect(soundEffectVolume);
    volumeText.textContent = volume;
    if(volume > 50){
        volumeImg.src = "img/thesound.png";
    } else if (volume <= 50 && volume != 0){
        volumeImg.src = "img/thehelfsound.png";
    } else {
        volumeImg.src = "img/thenosound.png";
        currentEffect = 0.5;
    }
    console.log("soundEffectVolume: "+hoverSound.volume);
});

// 畫面選單切換設定

function changePageToIntroduction(){
    entry.style.display = "none";
    gameIntroduce.style.display = "flex";
    playRegion.style.display="grid";
}

function changePageToSetting(){
    entry.style.display = "none";
    gameSetting.style.display = "flex";
    playRegion.style.display="grid";
}

function backToEntry(){
    initialPage.style.display = "none";
    gameIntroduce.style.display = "none";
    gameSetting.style.display = "none";
    entry.style.display = "flex";
    passPage.style.display = "none";
    fillPage.style.display = "none";    
    winPage.style.display ="none";
    document.querySelector(".time_and_score").style.display = "none";
    console.log("countSound.volume: "+countSound.volume);
}




// 難度調整
const difficultyButton = document.querySelectorAll(".difficulty_button");
for(let i=0;i<difficultyButton.length;i++){
    difficultyButton[i].addEventListener("click",()=>{
        difficultyButton.forEach(btn => {
            btn.classList.remove("current_active");
        })
        difficultyButton[i].classList.add("current_active");
        selectedDifficultyNumber = difficultyButton[i].getAttribute("data-difficulty");
        currentDifficultyNumber = Number(selectedDifficultyNumber)+Number(currentLevel);
        currentDifficulty = difficultyButton[i].textContent.trim();
        difficultyDisplay = document.querySelector("#mode");
        difficultyDisplay.textContent = `難度:${currentDifficulty}`;

    })
}


// 遊戲功能函數

// 更新分數
function updateScore() {
    document.querySelector('.score').textContent = `Score: ${score}`;
}


// 地鼠選位函數
function RandomPosition() {
    const sets = document.querySelectorAll(".set");
    let randomIndex;
    do{
       randomIndex = Math.floor(Math.random()*sets.length);
    }while(sets[randomIndex].querySelector(".gopher").classList.contains("occupied"));
    const displaynumber = randomIndex+1;
    gophercount++;
    console.log('第'+gophercount+"隻地鼠選到第"+displaynumber+'個洞');
    return sets[randomIndex];
}

function randomstaytime(min,max){
    return Math.random()*(max-min)+min;
}


// 清除地鼠躲藏事件功能檢查函數
function debug1(eventA,numberA){
    clearTimeout(eventA);
    console.log("清除第"+numberA+"隻地鼠躲藏事件");
}


// 遊戲主要功能函數
function ShowGopher(){
    const set = RandomPosition();
    const gopher = set.querySelector(".gopher");
    const badGopherImg = gopher.querySelector('img[src="img/badgopher.png"]');
    const goodGopherImg = gopher.querySelector('img[src="img/goodgopher.png"]');
    const dizzyBadGopherImg = gopher.querySelector('img[src="img/dizzybadgopher.png"]');
    const dizzyGoodGopherImg = gopher.querySelector('img[src="img/dizzygoodgopher.png"]');
    const currentgopher = gophercount;
    const IsGoodGopher = Math.random() > 0.8;
    if(IsGoodGopher){
        goodGopherImg.style.display = "block";
        badGopherImg.style.display = "none";
        dizzyBadGopherImg.style.display = "none"
        dizzyGoodGopherImg.style.display = "none"
        console.log("第"+currentgopher+"隻地鼠是好地鼠");
    }
    else{
        goodGopherImg.style.display = "none";
        badGopherImg.style.display = "block";
        dizzyBadGopherImg.style.display = "none"
        dizzyGoodGopherImg.style.display = "none"
        console.log("第"+currentgopher+"隻地鼠是壞地鼠");
    }

    gopher.classList.remove("hide");
    gopher.classList.add("show");
    gopher.classList.add("occupied");
    hoverSound.play();
    let countNumber = 1;
    const gopherstay = setInterval(
        ()=>{
            console.log("第"+currentgopher+"隻地鼠停留第"+countNumber+"秒");
            countNumber++;
        },1000
    )

    // 地鼠躲藏事件函數 
    const unhitting = setTimeout( () =>{
        if(gopher.classList.contains("show")){
            gopher.classList.remove("show");
            gopher.classList.add("hide");
            clearInterval(gopherstay);
            console.log("第"+currentgopher+"隻地鼠躲起來了");
            setTimeout(()=>{gopher.classList.remove("occupied");},750);
        } else {
            // 不該出現的提示
            console.log("成功擊打第"+currentgopher+"隻地鼠");
        }
    },randomstaytime(2000/currentDifficultyNumber,3000/currentDifficultyNumber));

    console.log("第"+currentgopher+"隻地鼠爬出來了！");

    const hitRegion = set.querySelector(".hit_region");
    
    // 打擊效果
    hitRegion.onclick = function(e){
        if(gopher.classList.contains("show")){
            debug1(unhitting,currentgopher);
            hitRegion.onclick = null;
            
            hitButtonSound.play();
            
            //攜帶裝置動畫
            const hammer = hitRegion.querySelector(".hammer");
            hammer.style.display = "block";    
            hammer.classList.add("hitting");
            hitRegion.querySelector(".hitting").addEventListener("animationend",()=>{
                setTimeout(()=>{
                    hammer.style.display = "none"; 
                },300);                               
            },{once:true});

            if(IsGoodGopher){
                score -=3;
                
                const span =document.createElement("span");
                span.className="getpoint";
                span.textContent="-3";
                span.style.left=`${e.clientX}px`;
                span.style.top=`${e.clientY-40}px`;
                span.style.color="red";
                    document.querySelector(".game_region").appendChild(span);
                requestAnimationFrame(
                    ()=>{
                        span.style.transform="translateY(-40px)";
                        span.style.opacity = "0";
                    }
                )
                span.addEventListener("transitioned", ()=>{
                    span.remove();
                });



                goodGopherImg.style.display ="none";
                dizzyGoodGopherImg.style.display ="block";
                
                setTimeout(() => {
                    gopherHert.play();
                }, 100);
                
                
                console.log("打到第"+currentgopher+"隻地鼠了，他是好地鼠，扣分");
                clearInterval(gopherstay);
            } else {
                score++;
                
                const span =document.createElement("span");
                span.className="getpoint";
                span.textContent="+1";
                span.style.left=`${e.clientX}px`;
                span.style.top=`${e.clientY-40}px`;
                document.querySelector(".game_region").appendChild(span);
                requestAnimationFrame(
                    ()=>{
                        span.style.transform="translateY(-40px)";
                        span.style.opacity = "0";
                    }
                )
                span.addEventListener("transitionend", ()=>{
                    span.remove();
                });

                badGopherImg.style.display = "none";
                dizzyBadGopherImg.style.display = "block";
                
                
                setTimeout(() => {
                    gopherHert.play();
                }, 100);


                console.log("打到第"+currentgopher+"隻地鼠了，他是壞地鼠，加分");
                clearInterval(gopherstay);
            }
            
            updateScore();            
            setTimeout( () => {
                gopher.classList.remove("show");
                gopher.classList.add("hide");
                console.log("第"+currentgopher+"隻地鼠被打回家了");
                setTimeout(()=>{gopher.classList.remove("occupied");},750);                
            },50);
        }   
    }; 
}


// 時間控制函數
function randomInterval(min,max){
        return Math.random()*(max-min)+min;
}


function countdown(toDoFunction){
    document.querySelector(".time_and_score").style.display = "block";
    passPage.style.display ="none";
    fillPage.style.display = "none";
    playRegion.style.display ="grid";
    const countPage = document.querySelector(".count_page");
    
    entry.style.display ="none";
    const countNumber = document.querySelector(".count_page_text_container span");
    let currentNumber = 3;
    countNumber.textContent= `${currentNumber}`;
    countNumber.classList.add("animate_big");
    // setTimeout(() => {
    //     countNumber.classList.remove("animate_big");
    //     }, 500);
    countSound.play();
    countPage.style.display= "flex";

    
    const countDownFunction = setInterval(()=>{
        
        // countNumber.classList.add("animate_big");
        currentNumber -= 1;
        countNumber.textContent= `${currentNumber}`;
        if(currentNumber > 0){countSound.play();};
        countNumber.classList.add("animate_big");
        // setTimeout(() => {
        //     countNumber.classList.remove("animate_big");
        //     }, 500);
        // countSound.play();
        // setTimeout(() => {
        //     countNumber.classList.remove("animate_big");
        // }, 300);
        
    },1000)
    setTimeout(() => {
        clearInterval(countDownFunction);
        startSound.play();
        countNumber.textContent= "Start!"
        toDoFunction();
    }, 3000);
    setTimeout(() => {
        countPage.style.display= "none";
    }, 4000);
}


// 遊戲開始函數

function countDown_and_start(){
    countdown(start);
}

function start() {
    entry.style.display ="none";
    passPage.style.display = "none";
    fillPage.style.display = "none";
    document.querySelector(".time_and_score").style.display = "block";
    score = 0;
    updateScore();
    gophercount = 0;
    let currentTime = levelTimeSet[currentLevel];
    timer.textContent = `Timer: ${currentTime/1000}`;
    // 計時器
    const timerFunction = setInterval(()=>{
        currentTime -= 1000;
        timer.textContent = `Timer: ${currentTime/1000}`;  
    },1000)
    const interval = setInterval(ShowGopher,randomInterval(1000/currentDifficultyNumber,1500/currentDifficultyNumber)); 
    setTimeout(()=>{
        clearInterval(interval);
        clearInterval(timerFunction);
        console.log("currentLevel="+currentLevel);
        checkWin();
        },levelTimeSet[currentLevel]);
    console.log("目前設定:");
    let Level = currentLevel+1;
    console.log("第"+Level+"關");
    console.log("關卡難度指數="+currentDifficultyNumber);
    console.log("關卡限時"+currentTime/1000+"秒");
    console.log("地鼠出沒頻率:"+1000/currentDifficultyNumber/1000+"秒到"+1500/currentDifficultyNumber/1000+"秒");
    console.log("地鼠停留時間:"+2000/currentDifficultyNumber/1000+"秒到"+3000/currentDifficultyNumber/1000+"秒");
}




// 檢查通關分數函數
function checkWin(){
    if(score >= 1){
        if(currentLevel < 2){
            currentLevel++;
            passPage.style.display = "flex";
            playRegion.style.display ="none";
            passSound.play();
            currentDifficultyNumber = Number(selectedDifficultyNumber)+Number(currentLevel);
        }else{
            winPage.style.display = "flex";
            playRegion.style.display ="none";
            victorySound.play();
            currentLevel = 0;
            currentDifficultyNumber = 1;
        }
    }else{
        fillPage.style.display = "flex";
        playRegion.style.display ="none";
        fillSound.play();
        currentLevel = 0
    }
}


