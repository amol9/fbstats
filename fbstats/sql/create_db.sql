create table stream (
	post_id 		varchar(40) primary key,
	source_id 		varchar(40),
	created_time		integer,
	type 			integer,
	like_count 		integer,
	comment_count		integer,
	is_popular 		integer,
	message 		text,
	share_count		integer,
	permalink 		varchar(120) unique,
	update_likes		integer,
	update_comments		integer,
	class1 			varchar(15),
	class2 			varchar(15),  
	class3 			varchar(15) 
);	/* date? */

create table user (
	id				varchar(40) primary key, 	
	first_name			varchar(40),
	middle_name			varchar(40),
	last_name			varchar(40),
	sex				character(1),		
	relationship_status		varchar(30),
	pic				varchar(100),
	significant_other_id		varchar(40),
	age_range			varchar(10),
	birthday_date			varchar(10),
	current_location		varchar(50),
	friend_count			integer,
	hometown_location		varchar(50),
	deleted			integer
);

create table device (
	user_id					varchar(40),
	os					varchar(30),
	hardware				varchar(30),
	PRIMARY KEY (user_id, os)
);

create table like (
	post_id 	varchar(40),
	user_id		varchar(40),
	PRIMARY KEY (post_id, user_id)
);

create table comment (
	comment_id	varchar(40) primary key,
	post_id		varchar(40),
	user_id		varchar(40)
);

create table job_period (
	start_time	integer,
	end_time	integer,
	get_count	integer
);

CREATE TABLE photo (
	photo_id	varchar(50) PRIMARY KEY,
	album_id	varchar(50),
	caption		text,
	comment_count	integer,
	like_count	integer,
	created_time	integer,
	link		varchar(150),
	owner_id	varchar(40),
	place_id	varchar(40),
	src_big		varchar(150),
	update_likes	integer,
	update_comments	integer
);

CREATE TABLE access (
	token		text,
	expiry		integer
);


CREATE TRIGGER del_stream_like_comment DELETE ON stream
BEGIN
	DELETE FROM likes WHERE post_id = old.post_id;
	DELETE FROM comment WHERE post_id = old.post_id;
END;
 

/*
type	int32	

The type of this story. Possible values are:

    11 - Group created
    12 - Event created
    46 - Status update
    56 - Post on wall from another user
    66 - Note created
    80 - Link posted
    128 -Video posted
    247 - Photos posted
    237 - App story
    257 - Comment created
    272 - App story
    285 - Checkin to a place
    308 - Post in Group

--

likes 	struct

count		unsigned int32		The total number of likes
friends		array<id>			List of friends' user IDs who liked the post
user_likes	bool				Whether the user has liked this post

*/
