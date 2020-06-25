var api='http://tootal.xyz:5000/api/'
var statusArray=[];
function showSubmitPanel(){
    document.getElementById('panel-shadow').style.display='block';
    document.getElementById('submit-panel').style.display='block';
    document.getElementById('menu').style.display='none';
}
function hideSubmitPanel(){
    document.getElementById('menu').style.display='block';
    document.getElementById('panel-shadow').style.display='none';
    document.getElementById('submit-panel').style.display='none';
}
function lang2content(lang){
    var content_type;
    switch(lang){
        case 'Python':
            content_type='text/x-python';
            break;
        case 'C':
            content_type='text/x-csrc';
            break;
        case 'C++':
            content_type='text/x-c++src';
            break;
        case 'Java':
            content_type='text/x-java';
            break;
        default:
            content_type='text/plain';
    }
    return content_type;
}
function content2lang(content){
    var lang;
    switch(content){
        case 'text/x-python':
            lang='Python';
            break;
        case 'text/x-csrc':
            lang='C';
            break;
        case 'text/x-c++src':
            lang='C++';
            break;
        case 'text/x-java':
            lang='Java';
            break;
        default:
            lang='text';
    }
    return lang;
}
function submitSolution(){
    var submit_solution=document.getElementById('submit-solution');
    var submit_language=document.getElementById('submit-language');
    // console.log(fetch);
    fetch(api+'solution',{
        method: 'POST',
        mode: 'cors',
        headers: {
            'Content-Type': lang2content(submit_language.value)
        },
        body: submit_solution.value
    }).then(function(res){
        return res.text();
    }).then(function(res){
        // console.log(res);
        if(res=='ok'){
            hideSubmitPanel();
            showStatusPanel();
        }else{
            console.log('Submit Failed!');
        }
    })
}
function showStatusPanel(){
    document.getElementById('panel-shadow').style.display='block';
    document.getElementById('status-panel').style.display='block';
    document.getElementById('menu').style.display='none';
    getStatus();
}
function hideStatusPanel(){
    document.getElementById('menu').style.display='block';
    document.getElementById('panel-shadow').style.display='none';
    document.getElementById('status-panel').style.display='none';
}
function getStatus(){
    // console.log('getStatus()');
    fetch(api+'status')
    .then(function(res){
        return res.json();
    }).then(function(res){
        // console.log(res);
        statusArray=res;
        // console.log(statusArray);
        showStatus();
    })
}
function showStatus(){
    // console.log('showStatus()');
    var statusTable=document.getElementById('status-table');
    var statusTableChilds=statusTable.children;
    var i=1;
    while(i<statusTableChilds.length){
        statusTable.removeChild(statusTableChilds[i]);
    }
    for(i=statusArray.length-1;i>=0;i--){
        var row=createStatusRow(statusArray[i]);
        statusTable.appendChild(row);
    }
}
function createStatusRow(statusRow){
    var row=document.createElement('tr');
    var time_col=document.createElement('td');
    var lang_col=document.createElement('td');
    var status_col=document.createElement('td');
    time_col.innerHTML=nearTime(statusRow['time']);
    lang_col.innerHTML=statusRow['lang'];
    status_col.innerHTML=statusRow['status'];
    row.appendChild(time_col);
    row.appendChild(status_col);
    row.appendChild(lang_col);
    return row;
}
function nearTime(t){
    // console.log('nearTime');
    // console.log(t);
    var now=new Date();
    var pre=new Date();
    pre.setFullYear(t.substring(0,4));
    pre.setMonth(t.substring(4,6));
    pre.setDate(t.substring(6,8));
    pre.setHours(t.substring(8,10));
    pre.setMinutes(t.substring(10,12));
    pre.setSeconds(t.substring(12,14));
    if(now.getFullYear()-pre.getFullYear()>=1){
        return String(now.getFullYear()-pre.getFullYear())+'年前';
    }else if(now.getMonth()-pre.getMonth()>=1){
        return String(now.getMonth()-pre.getMonth())+'月前';
    }else if(now.getDate()-pre.getDate()>=1){
        return String(now.getDate()-pre.getDate())+'天前';
    }else if(now.getHours()-pre.getHours()>=1){
        return String(now.getHours()-pre.getHours())+'小时前';
    }else if(now.getMinutes()-pre.getMinutes()>=1){
        return String(now.getMinutes()-pre.getMinutes())+'分钟前';
    }else if(now.getSeconds()-pre.getSeconds()>=1){
        return String(now.getSeconds()-pre.getSeconds())+'秒前';
    }else{
        return '刚刚';
    }
}
