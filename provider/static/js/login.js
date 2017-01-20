//global, filled by server on page
var server_errors;

$(document)
.ready(function() {
  $('.ui.form')
    .form({
      fields: {
        email: {
          identifier  : 'email',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter your e-mail'
            },
            {
              type   : 'email',
              prompt : 'Please enter a valid e-mail'
            }
          ]
        },
        password: {
          identifier  : 'password',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please enter your password'
            },
            {
              type   : 'length[6]',
              prompt : 'Your password must be at least 6 characters'
            }
          ]
        },
        confirmpassword: {
          identifier  : 'confirmpassword',
          rules: [
            {
              type   : 'empty',
              prompt : 'Please confirm your password'
            }
          ]
        }
      }
    })
  ;

  if (server_errors.length > 0) {
    $('.form').form('add errors', server_errors)
  }
})
;