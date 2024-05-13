document.addEventListener('DOMContentLoaded', () => {
    let post_form = document.querySelector('#post-form');
    post_form.querySelector('textarea[name="content"]').addEventListener('input', function() {
        this.style.height = '36px';
        this.style.height = this.scrollHeight+2+'px';
        let submit = post_form.querySelector('input[type="submit"]');
        if (this.value) submit.disabled = false;
        else submit.disabled = true;
    });
    post_form.addEventListener('submit', function() {
        fetch('/post', {
            method: 'POST',
            body: JSON.stringify({
                content: post_form.querySelector('textarea').value
            }),
            headers: {
                'X-CSRFToken': post_form.querySelector('input[name=csrfmiddlewaretoken]').value,
            }
          })
    });
    document.querySelectorAll('.post-content').forEach(post => {
        post.style.height = '36px';
        post.style.height = post.scrollHeight+2+'px';
    });
});
let editing_post;
let editing_post_last_content;
document.addEventListener('click', function(event) {
    let target = event.target; 
    if (event.target.tagName == 'path')
    {
        target = event.target.parentElement.parentElement;
    }
    if (Array.from(target.classList).includes('like'))
    {
        fetch('/like', {
            method: 'POST',
            body: JSON.stringify({
                post: parseInt(target.dataset.post),
                like: target.dataset.like == "false"
            }),
            headers: {
                'X-CSRFToken': document.cookie.split('csrftoken=')[1].split(';')[0],
            }
          })
          .then(response => response.json())
          .then(data => {
            if (!data.error)
            {
                document.querySelectorAll(`.like[data-post="${target.dataset.post}"]`).forEach(el => {
                    if (el.style.display == 'none')
                    {
                        el.style.display = 'inline-block';
                    }
                    else 
                    {
                        el.style.display = 'none';
                    }
                });
                let likes = document.querySelector(`.likes-count-${target.dataset.post}`);
                likes.innerHTML = target.dataset.like == "true" ? parseInt(likes.innerHTML)-1 : parseInt(likes.innerHTML)+1;
            }
          })
    }
    // Edit post 
    else if (Array.from(target.classList).includes('edit-post-button'))
    {
        if (editing_post)
        {
            end_editing_post(editing_post);
        }
        editing_post = target.parentElement;
        let content = editing_post.querySelector('textarea');
        editing_post_last_content = content.value;
        content.disabled = false;
        content.style.border = "1px solid black";
        content.focus();
        content.selectionStart = content.value.length;

        let save = document.createElement('button');
        save.innerHTML = "Save";
        save.className = 'btn btn-primary edit-buttons';
        save.addEventListener('click', () => {
            fetch('/post-edit', {
                method: 'POST',
                body: JSON.stringify({
                    post: parseInt(target.dataset.postId),
                    content: content.value
                }),
                headers: {
                    'X-CSRFToken': document.cookie.split('csrftoken=')[1].split(';')[0],
                }
              })
              .then(result => result.json())
              .then(result => {
                if (!result.error) 
                {
                    editing_post_last_content = content.value;
                    end_editing_post(editing_post);
                }
              });
        })
        editing_post.append(save);

        content.addEventListener('input', function() {
            if (this.value) save.disabled = false;
            else save.disabled = true;
        });

        let cancel = document.createElement('button');
        cancel.innerHTML = "Cancel";
        cancel.className = 'btn btn-primary edit-buttons cancel-edit-button';
        cancel.addEventListener('click', () => end_editing_post(editing_post));
        editing_post.append(cancel);
    }
});
function end_editing_post(post)
{
    let content = post.querySelector('textarea');
    content.disabled = true;
    content.style.border = "none";
    content.value = editing_post_last_content;
    content.replaceWith(content.cloneNode());
    post.querySelectorAll('.edit-buttons').forEach(el => el.remove());
}