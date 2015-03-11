// Copyright Collab 2014-2015

!function ($)
{
	if (window.collab == undefined) window.collab = {};

	collab.PreviewWidget = function(elem, paths)
	{
		if (paths.length > 0)
		{
			require([
            	'wavesurfer',
            	'videojs',
            	'videojsWavesurfer',
            	'videojsPersistVolume'
			],
			function(wavesurfer, videojs, videojsWavesurfer, videojsPersistVolume)
			{
				this.elem = elem;
			    this.paths = paths;
			    this.lastElement = this.elem.parent().find('p.help');
			    this.select = this.elem.find('select');
	
			    var players = $("<div id='players' class='row' style='margin-left: 100px;'></div>"
			        ).insertAfter(this.lastElement);
	
			    var url, markup;
			    for (var index in this.paths)
			    {
			    	url = this.paths[index];
			    	markup = '';
	
			    	// AUDIO
			    	if (url.endsWith('mp3') || url.endsWith('oga'))
			    	{
			    		markup = '<audio id="myAudio' + index + '" class="video-js vjs-default-skin"></audio>';
			    		players.append(markup);
	
			    		var player = videojs("myAudio" + index,
						{
						    controls: true,
						    autoplay: false,
						    loop: false,
						    width: 400,
						    height: 200,
						    plugins: {
						        wavesurfer: {
						            src: url,
						            msDisplayMax: 10,
						            waveColor: "grey",
						            progressColor: "black",
						            cursorColor: "black",
						            hideScrollbar: true
						        },
						        persistvolume: {
						            namespace: 'collab_admin'
						        }
						    }
						});
			    		
			    		// change player background color
			    		player.el().style.backgroundColor = "#BDBBBC";
			    	}
			    	// SNAPSHOT
			    	else if (url.endsWith('png'))
			    	{
			    		markup = "<a href='" + url + "' target='_blank'><img src='" + url + "' title='" + url +
			    		    "' style='max-width: 600px; max-height: 480px; padding: 20px;'/></img></a>";
			    		players.append(markup);
			    	}
			    	// VIDEO
			    	else if (url.endsWith('webm') || url.endsWith('mp4'))
			    	{
			    		markup = '<video id="myVideo' + index + '" class="video-js vjs-default-skin"></video>';
			    		players.append(markup);
			    		
			    		// add video player
	                    var player = videojs("myVideo" + index,
	                    {
	                        controls: true,
	                        autoplay: false,
	                        loop: false,
	                        width: 320,
	                        height: 240,
	                        plugins: {
				                persistvolume: {
						            namespace: 'collab_admin'
						        }
				            }
	                    });
	                    player.src(url);
			    	}
			    }
			});
		}
	};
	
	String.prototype.endsWith = function(suffix) {
	    return this.indexOf(suffix, this.length - suffix.length) !== -1;
	};
}(window.jQuery)