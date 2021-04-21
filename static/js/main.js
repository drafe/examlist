
xl_file = document.getElementById('id_upload-file')

xl_file.addEventListener('change', ()=>{
    const data = xl_file.files[0]

   	/* get the workbook */
    const options={ type: 'array'};
    const workbook = XLSX.read(xl_file.files[0],  options);
	/* get the sheet name */
    const sheetName = workbook.SheetNames;
    console.log(sheetName)

    const url = URL.createObjectURL(data)

    console.log(url)
})

function copytable(el) {
    var urlField = document.getElementById(el)
    var range = document.createRange()
    range.selectNode(urlField)
    window.getSelection().addRange(range)
    document.execCommand('copy')
}
