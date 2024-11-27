var x = document.getElementById('show-pass');
var y = document.getElementById('pass');
var img = x.querySelector("img")
x.addEventListener('click' , function() {
   if(y.type === 'password'){
        y.type ='text';
        img.src='static/eye-close.svg';
   }else{
        y.type='password';
        img.src='static/eye-open.svg';
   }
 })