import os
from flask import Flask, render_template, request, redirect, url_for, flash, \
    Response, send_file
from flask_bootstrap import Bootstrap
import boto3
from filters import datetimeformat, file_type, sizeof_fmt
from transcribe import create_transcription, getFileURL, check_job_exist
import time
import urllib

S3_BUCKET = "itisprojectbucket" 
app = Flask(__name__)
Bootstrap(app)
app.jinja_env.filters['datetimeformat'] = datetimeformat
app.jinja_env.filters['file_type'] = file_type
app.jinja_env.filters['sizeof_fmt'] = sizeof_fmt
app.secret_key = 'secret'

@app.route('/player', methods=['POST'])
def player():
    key = request.form['key']
    file_info = os.path.splitext(key)
    file_name = file_info[0]
    return render_template('player.html', file_name = file_name)

@app.route('/') 
@app.route('/files')
def files():
    s3 = boto3.resource('s3')
    my_bucket = s3.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    return render_template('files.html', my_bucket=my_bucket, files=summaries)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    summaries = my_bucket.objects.all()
    file_exist = False

    if file.filename =='':
        flash('No selected file')
        return redirect(url_for('files'))

    for f in summaries:
        if f.key==file.filename:
            file_exist = True

    if file_exist == False:
        if file_type(file.filename.lower()) == "video/mp4":
            my_bucket.Object(file.filename).put(Body=file)
            #make the file public for access
            my_bucket.Object(file.filename).Acl().put(ACL='public-read')

            flash('File uploaded successfully')
            return redirect(url_for('files'))
        else:
            flash('Only mp4 file is accepted.')
            return redirect(url_for('files'))

    flash('The file already exist, please rename the file.')
    return redirect(url_for('files'))

@app.route('/delete', methods=['POST'])
def delete():
    key = request.form['key']

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)
    my_bucket.Object(key).delete()

    flash('File deleted successfully')
    return redirect(url_for('files'))

@app.route('/download', methods=['POST'])
def download():
    key = request.form['key']
    file_info = os.path.splitext(key)
    file_name = file_info[0]

    s3_resource = boto3.resource('s3')
    my_bucket = s3_resource.Bucket(S3_BUCKET)

    file_obj = my_bucket.Object(key).get()

    '''return Response(
        file_obj['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename={}".format(key)}
    )'''

    try:
        return send_file('static/'+file_name+'.vtt', attachment_filename=file_name+'.vtt', as_attachment=True)
    except:
        flash('video not transcribed')
        return redirect(url_for('files'))

@app.route('/transcribe/<job_name>')
def transcribe(job_name):
    #create the transcription job and supply the source video file
    create_transcription(job_name)

    url = getFileURL(job_name)

    file = urllib.request.urlopen(url)
    content = file.read().decode('utf-8')
    return render_template('createsrt.html', content = content, job_name = job_name)

@app.route('/subtitle/<job_name>', methods=['POST'])
def subtitle(job_name):
    key=request.form['key']

    #write the generated subtitle into a new .vtt file
    f = open( "/home/ubuntu/flaskapp/static/" + job_name + ".vtt", "w" , newline='')
    f.write(key)
    return redirect(url_for('files'))

@app.route('/loading',methods=['POST'])
def loading():
    key = request.form['key']

    file_info = os.path.splitext(key)
    job_name = file_info[0]

    #check if the job exist by checking the subtitle files exist
    if check_job_exist(job_name):
        flash('Job already exist, please check if it is the same file or rename the video')
        return redirect(url_for('files'))
    return render_template('loading.html', job_name = job_name)

if __name__ == '__main__':
    app.run(debug = True)
