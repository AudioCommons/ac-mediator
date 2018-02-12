Array.from($('body > div.back > div:nth-child(1) > div:nth-child(2) > table').children).map(x=>Array.from(x.children).map(x=>x.textContent.trim().replace(/(\s)+/g,' ')))

Array.from($('body > div.back > div:nth-child(1) > div:nth-child(2) > table').children).map(x=>x.textContent.trim().replace(/(\s)+/g,' ')).join('\n')
