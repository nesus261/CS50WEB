document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector('#compose-form').onsubmit = send_email;
  
  // By default, load the inbox
  load_mailbox('inbox');
});

// Add a listener to detect clicks on email messages and archive buttons
document.addEventListener('click', (event) => {
  if (event.target.className.includes('email-message'))
  {
    load_email(event.target.dataset.id);
  }
  else if (event.target.className.includes('email-archive-button'))
  {
    fetch(`/emails/${event.target.parentElement.dataset.id}`, {
      method: 'PUT',
      body: JSON.stringify({
          archived: event.target.dataset.archived == "false"
      })
    })
    .then(() => load_mailbox('inbox'))
  }
});

function send_email() {
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(response => response.json())
  .then(result => {
    if (result.error)
    {
      let alert = document.querySelector('#alert-compose-form');
      alert.innerHTML = result.error;
      alert.style.display = 'block';
    }
    else 
    {
      load_mailbox('sent');
    }
  });

  // Prevent default submission
  return false;
}

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-content').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  document.querySelector('#alert-compose-form').style.display = 'none';
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#email-content').style.display = 'none';
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Load emails from the selected mailbox 
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      if (!emails.error)
      {
        // Show the mailbox name
        document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
      
        emails.forEach(email => {
          let div = document.createElement('div');
          div.className = `alert alert-${email.read ? 'dark' : 'light border'} mb-2 email-message`;
          div.dataset.id = email.id;
          // Add div content - show sender, archive button, subject and timestamp
          div.innerHTML = `
            <b>Sender: ${email.sender}</b>
            ${mailbox == 'sent' ? '' : 
              `<button 
                data-archived="${email.archived}"
                class='btn btn-${email.read ? 'light' : 'dark'} float-right email-archive-button'>
                  ${email.archived ? 'Unarchive' : 'Archive'}
              </button>`}
            <br><b>Subject: ${email.subject}</b><br>
            ${email.timestamp}`;
          document.querySelector('#emails-view').append(div);
        });
      }
  });
}

function load_email(id) 
{
  document.querySelector('#email-content').style.display = 'block';
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Display information about email 
  fetch(`/emails/${id}`)
  .then(response => response.json())
  .then(email => {
      if (!email.error)
      {
        document.querySelector('#email-content-sender').innerHTML = email.sender;
        document.querySelector('#email-content-recipients').innerHTML = email.recipients.join();
        document.querySelector('#email-content-subject').innerHTML = email.subject;
        document.querySelector('#email-content-timestamp').innerHTML = email.timestamp;
        let body = document.querySelector('#email-content-body');
        body.innerHTML = email.body;
        body.style.height = body.scrollHeight+'px';
        document.querySelector('#email-reply').onclick = () => {

          // Show compose view and hide other views
          document.querySelector('#emails-view').style.display = 'none';
          document.querySelector('#email-content').style.display = 'none';
          document.querySelector('#compose-view').style.display = 'block';
        
          // Pre-fill composition fields
          document.querySelector('#compose-recipients').value = document.querySelector('#compose-form input[disabled]').value != email.sender ? 
                                                                email.sender : email.recipients.join();
          document.querySelector('#compose-subject').value = email.subject.startsWith('Re: ') ? 
                                                             email.subject : `Re: ${email.subject}`;
          document.querySelector('#compose-body').value = `On ${email.timestamp} ${email.sender} wrote: \n\n${email.body}\n\n`;
          document.getElementById(fieldId).style.height = document.getElementById(fieldId).scrollHeight+'px';

          // Hide alert if is displayed 
          document.querySelector('#alert-compose-form').style.display = 'none';

        };
      }
  });

  // Mark an email as read
  fetch(`/emails/${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
}