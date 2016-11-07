var getJSON = function(url) {
  return new Promise(function(resolve, reject) {
    var xhr = new XMLHttpRequest();
    xhr.open('get', url, true);
    xhr.responseType = 'json';
    xhr.onload = function() {
      if (xhr.status === 200) {
        resolve(xhr);
      } else {
        reject(xhr);
      }
    };
    xhr.send();
  });
};